import inspect
from typing import Annotated, override

import fastmcp
import langchain_community.utilities
import sqlalchemy as sa

from bir_mcp.config import SqlContext
from bir_mcp.core import BaseMcp, build_readonly_tools
from bir_mcp.utils import split_schema_table


class SQL(BaseMcp):
    def __init__(
        self,
        sql_context: SqlContext,
        sample_rows_in_table_info: int = 5,
        timezone: str = "UTC",
    ):
        super().__init__(timezone=timezone)
        self.sql_context = sql_context
        self.engine = self.sql_context.connection.get_engine()
        self.databases = sql_context.get_langchain_sql_databases_by_schema(
            sample_rows_in_table_info=sample_rows_in_table_info,
        )

    @override
    def get_tag(self):
        return f"sql_{self.sql_context.name}"

    @override
    def get_mcp_server_without_components(self):
        server = fastmcp.FastMCP(
            name="MCP server with SQL tools",
            instructions=inspect.cleandoc("""
                Contains tools to work with SQL databases.
            """),
        )
        return server

    @override
    def get_mcp_tools(self, max_output_length: int | None = None, tags: set[str] | None = None):
        read_tools = [
            self.get_database_info,
            self.get_available_table_names,
            self.get_table_info,
            self.execute_query,
        ]
        tools = build_readonly_tools(read_tools, max_output_length=max_output_length, tags=tags)
        return tools

    def get_schema_database(
        self, schema: str | None = None
    ) -> langchain_community.utilities.SQLDatabase:
        if not (database := self.databases.get(schema)):
            raise ValueError(f"Schema {schema} is not available.")

        return database

    def get_schema_database_and_table(
        self, schema_table: str
    ) -> tuple[langchain_community.utilities.SQLDatabase, str]:
        schema, table = split_schema_table(schema_table)
        database = self.get_schema_database(schema)
        return database, table

    def get_available_table_names(self) -> dict:
        """Get available schema-qualified table names."""
        tables = self.sql_context.schema_tables
        tables = {"tables": tables}
        return tables

    def get_table_info(self, table: str) -> dict:
        """Get SQL table info, such as its DDL statement and first few rows."""
        database, table = self.get_schema_database_and_table(table)
        table_info = database.get_table_info(table_names=[table])
        table_info = {"table_info": table_info}
        return table_info

    def execute_query(self, query: str, schema: str | None = None) -> dict:
        """
        Execute an SQL query and return the result.
        Currently a query cannot reference tables from different schemas.
        """
        database = self.get_schema_database(schema)
        result = database.run(query)
        result = {"result": result}
        return result

    def get_database_info(self) -> dict:
        """Get info about the database, such as its dialect and version."""
        inspector = sa.inspect(self.engine)
        dialect = inspector.dialect
        info = {
            "dialect_name": dialect.name,
        }
        if dialect.server_version_info:
            info["server_version"] = ".".join(map(str, dialect.server_version_info))

        return info
