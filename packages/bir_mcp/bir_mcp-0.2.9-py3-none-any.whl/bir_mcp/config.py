import enum
import warnings
from typing import Self, override

import langchain_community.utilities
import pydantic
import sqlalchemy as sa
import yaml

from bir_mcp.hashicorp import ConsulKeyValue
from bir_mcp.utils import set_ssl_cert_file_from_cadata, split_schema_table


class Driver(enum.StrEnum):
    oracle = enum.auto()
    postgresql = enum.auto()

    @property
    def name_and_package(self):
        match self:
            case Driver.oracle:
                return "oracle+oracledb"
            case Driver.postgresql:
                return "postgresql+psycopg"

        assert False


class SqlConnection(pydantic.BaseModel):
    driver: Driver
    host: str
    port: int
    database: str | None = None
    username: str
    password: str
    parameters: dict[str, str] | None = None

    @property
    def url(self) -> sa.URL:
        url = sa.URL.create(
            drivername=self.driver.name_and_package,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
            query=self.parameters or {},
        )
        return url

    def get_engine(self) -> sa.Engine:
        engine = sa.create_engine(self.url)
        return engine


class SqlContext(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(str_to_lower=True)

    name: str | None = None
    connection: SqlConnection
    schema_tables: list[str] = []

    @pydantic.model_validator(mode="after")
    def _validate(cls, self):
        self.get_langchain_sql_databases_by_schema()
        return self

    def get_tables_by_schema(self) -> dict[str | None, list[str]]:
        tables_by_schema = {}
        for table in self.schema_tables:
            table = table.lower()
            schema, table = split_schema_table(table)
            tables_by_schema.setdefault(schema, []).append(table)

        return tables_by_schema

    def get_langchain_sql_databases_by_schema(
        self, **kwargs
    ) -> dict[str | None, langchain_community.utilities.SQLDatabase]:
        inspector = sa.inspect(self.connection.get_engine())
        databases = {}
        for schema, tables in self.get_tables_by_schema().items():
            available_tables = set(inspector.get_table_names(schema))
            if missing_tables := set(tables) - available_tables:
                warnings.warn(
                    f"The following tables were not found in schema {schema} of SQL context "
                    f"{self.name} and will be ignored:\n"
                    f"{'\n'.join(sorted(missing_tables))}."
                )

            tables = sorted(set(tables) & available_tables)
            database = langchain_community.utilities.SQLDatabase(
                engine=self.connection.get_engine(),
                schema=schema,
                include_tables=[t.lower() for t in tables],
                **kwargs,
            )
            databases[schema] = database

        return databases


class SystemManagedConfig(pydantic.BaseModel):
    gitlab_private_token: str | None = None
    grafana_username: str | None = None
    grafana_password: str | None = None
    jira_token: str | None = None
    gitlab_url: str = "https://gitlab.kapitalbank.az"
    grafana_url: str = "https://yuno.kapitalbank.az"
    jira_url: str = "https://jira-support.kapitalbank.az"
    ca_file: str | None = None
    sql_contexts: list[SqlContext] = []

    @classmethod
    def from_consul(
        cls, consul_host: str, consul_key: str, consul_token: str | None = None
    ) -> Self:
        consul_key_value = ConsulKeyValue(host=consul_host, key=consul_key, token=consul_token)
        value = consul_key_value.load()
        config = yaml.safe_load(value)
        config = cls(**config)
        return config

    @override
    def model_post_init(self, context) -> None:
        if self.ca_file:
            set_ssl_cert_file_from_cadata(self.ca_file)
