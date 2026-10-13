from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.schema import CreateSchema

from pnao_client.config import DATABASE_URL, DB_SCHEMA
from pnao_client.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

target_metadata = Base.metadata


def include_name(name, type_, parent_names) -> bool:
    """Reflect only model tables in the configured application schema."""
    default_schema = context.get_context().dialect.default_schema_name
    if type_ == "schema":
        return (name if name is not None else default_schema) == DB_SCHEMA
    if type_ == "table":
        schema = parent_names.get("schema_name")
        schema = schema if schema is not None else default_schema
        return schema == DB_SCHEMA and any(
            table.name == name and table.schema == DB_SCHEMA
            for table in target_metadata.tables.values()
        )
    return True


def include_object(object_, name, type_, reflected, compare_to) -> bool:
    """Exclude tables outside the configured application schema."""
    if type_ == "table":
        return include_name(object_.schema, "schema", {})
    return True


def process_revision_directives(context_, revision, directives) -> None:
    """Keep generated operations qualified even for the default schema."""
    def qualify(operation):
        if hasattr(operation, "schema") and operation.schema is None:
            operation.schema = DB_SCHEMA
        for child in getattr(operation, "ops", ()):
            qualify(child)

    for script in directives:
        for operations in script.upgrade_ops_list + script.downgrade_ops_list:
            qualify(operations)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_schemas=True,
        include_name=include_name,
        include_object=include_object,
        version_table_schema=DB_SCHEMA,
        process_revision_directives=process_revision_directives,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.execute(CreateSchema(DB_SCHEMA, if_not_exists=True))
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        {"sqlalchemy.url": DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,
            include_object=include_object,
            version_table_schema=DB_SCHEMA,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.execute(CreateSchema(DB_SCHEMA, if_not_exists=True))
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
