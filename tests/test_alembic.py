import runpy
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from sqlalchemy.dialects import postgresql


@pytest.mark.parametrize("offline", [False, True])
def test_schema_is_created_in_transaction_before_migrations(monkeypatch, offline):
    monkeypatch.setattr("pnao_client.config.DB_SCHEMA", "pnao")
    context = MagicMock()
    context.config.config_file_name = None
    context.is_offline_mode.return_value = offline
    events = []
    context.begin_transaction.return_value.__enter__.side_effect = lambda: (
        events.append("begin")
    )
    context.begin_transaction.return_value.__exit__.side_effect = lambda *args: (
        events.append("end")
    )
    context.execute.side_effect = lambda statement: events.append(
        str(statement.compile(dialect=postgresql.dialect()))
    )
    context.run_migrations.side_effect = lambda: events.append("migrate")
    monkeypatch.setattr("alembic.context", context)
    monkeypatch.setattr("sqlalchemy.engine_from_config", MagicMock())

    runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "pnao_client/migrations/env.py")
    )

    assert events == [
        "begin",
        "CREATE SCHEMA IF NOT EXISTS pnao",
        "migrate",
        "end",
    ]
    assert context.configure.call_args.kwargs["version_table_schema"] == "pnao"


@pytest.mark.parametrize("upgrade", [True, False])
def test_updated_at_migration_only_alters_column(monkeypatch, upgrade):
    monkeypatch.setattr("pnao_client.config.DB_SCHEMA", "pnao")
    import io

    from alembic import command
    from alembic.config import Config

    output = io.StringIO()
    config = Config(output_buffer=output)
    config.set_main_option(
        "script_location",
        str(Path(__file__).resolve().parents[1] / "pnao_client/migrations"),
    )
    config.set_main_option("sqlalchemy.url", "postgresql://localhost/test")
    if upgrade:
        command.upgrade(config, "0b618d095e8c:5bd4e261e235", sql=True)
    else:
        command.downgrade(config, "5bd4e261e235:0b618d095e8c", sql=True)
    sql = output.getvalue()
    if upgrade:
        assert (
            "ALTER TABLE pnao.raw_data ADD COLUMN updated_at "
            "TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL"
        ) in sql
    else:
        assert "ALTER TABLE pnao.raw_data DROP COLUMN updated_at" in sql
    assert "CREATE TABLE pnao.raw_data" not in sql
    assert "DROP TABLE pnao.raw_data" not in sql
    assert "CREATE INDEX" not in sql
    assert "DROP INDEX" not in sql


@pytest.mark.parametrize("default_schema", ["pnao", "public"])
def test_autogenerate_recognizes_existing_table_in_default_schema(
    monkeypatch, default_schema
):
    import sqlalchemy as sa
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    # SQLite exercises Alembic's real comparison without contacting PostgreSQL.
    # Its main database stands in for the connection's default schema.
    monkeypatch.setattr("pnao_client.config.DB_SCHEMA", "pnao")
    context = MagicMock()
    context.config.config_file_name = None
    context.is_offline_mode.return_value = True
    monkeypatch.setattr("alembic.context", context)
    env = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "pnao_client/migrations/env.py")
    )
    engine = sa.create_engine("sqlite://")
    with engine.connect() as connection:
        connection.exec_driver_sql("CREATE TABLE raw_data (id INTEGER NOT NULL PRIMARY KEY)")
        connection.dialect.default_schema_name = default_schema
        metadata = sa.MetaData()
        sa.Table(
            "raw_data", metadata, sa.Column("id", sa.Integer, primary_key=True),
            schema=default_schema,
        )
        migration_context = MigrationContext.configure(
            connection,
            opts={"include_schemas": True, "include_name": env["include_name"]},
        )
        env["include_name"].__globals__["target_metadata"] = metadata
        context.get_context.return_value = migration_context
        assert env["include_name"](None, "schema", {}) == (default_schema == "pnao")
        assert not env["include_name"]("other", "schema", {})
        if default_schema == "pnao":
            assert compare_metadata(migration_context, metadata) == []
    engine.dispose()


@pytest.mark.parametrize("schema", ["pnao", "custom_schema", "main"])
def test_autogenerate_ignores_tables_and_models_outside_pnao(monkeypatch, schema):
    import sqlalchemy as sa
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    monkeypatch.setattr("pnao_client.config.DB_SCHEMA", schema)
    context = MagicMock()
    context.config.config_file_name = None
    context.is_offline_mode.return_value = True
    monkeypatch.setattr("alembic.context", context)
    env = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "pnao_client/migrations/env.py")
    )
    engine = sa.create_engine("sqlite://")
    with engine.connect() as connection:
        if schema != "main":
            connection.exec_driver_sql(f"ATTACH DATABASE ':memory:' AS {schema}")
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS other")
        connection.exec_driver_sql(
            f"CREATE TABLE {schema}.raw_data (id INTEGER NOT NULL PRIMARY KEY)"
        )
        if schema != "main":
            connection.exec_driver_sql("CREATE TABLE raw_data (unrelated TEXT)")
        for table in ["spatial_ref_sys", "alembic_version", "unrelated"]:
            connection.exec_driver_sql(f"CREATE TABLE {schema}.{table} (id INTEGER)")
        connection.exec_driver_sql("CREATE TABLE other.raw_data (unrelated TEXT)")
        metadata = sa.MetaData()
        sa.Table(
            "raw_data", metadata, sa.Column("id", sa.Integer, primary_key=True),
            schema=schema,
        )
        # Even models outside pnao must not produce CREATE TABLE operations.
        outside_schemas = ["other"] if schema == "main" else [None, "other"]
        for outside_schema in outside_schemas:
            sa.Table(
                "new_table", metadata, sa.Column("id", sa.Integer),
                schema=outside_schema,
            )
        migration_context = MigrationContext.configure(
            connection,
            opts={
                "include_schemas": True,
                "include_name": env["include_name"],
                "include_object": env["include_object"],
            },
        )
        env["include_name"].__globals__["target_metadata"] = metadata
        context.get_context.return_value = migration_context
        assert compare_metadata(migration_context, metadata) == []
        metadata.tables[f"{schema}.raw_data"].append_column(sa.Column("test", sa.String(50)))
        diffs = compare_metadata(migration_context, metadata)
        assert len(diffs) == 1
        assert diffs[0][:3] == (
            "add_column", None if schema == "main" else schema, "raw_data"
        )
        assert diffs[0][3].name == "test"
        from alembic.autogenerate import produce_migrations

        script = produce_migrations(migration_context, metadata)
        env["process_revision_directives"](migration_context, None, [script])
        for operations in [script.upgrade_ops, script.downgrade_ops]:
            assert operations.ops[0].schema == schema
            assert operations.ops[0].ops[0].schema == schema
    engine.dispose()


def test_generated_test_revision_only_changes_pnao_raw_data():
    import io

    from alembic import command
    from alembic.config import Config

    output = io.StringIO()
    config = Config(output_buffer=output)
    config.set_main_option(
        "script_location",
        str(Path(__file__).resolve().parents[1] / "pnao_client/migrations"),
    )
    config.set_main_option("sqlalchemy.url", "postgresql://localhost/test")
    command.upgrade(config, "5bd4e261e235:eaffb6de0652", sql=True)
    sql = output.getvalue()
    assert "ALTER TABLE pnao.raw_data ADD COLUMN test" in sql
    assert "DROP TABLE" not in sql
    assert "spatial_ref_sys" not in sql
