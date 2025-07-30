import enum
import functools
import inspect
import warnings
from typing import Annotated

import fastmcp
import typer

import bir_mcp.atlassian
import bir_mcp.git_lab
import bir_mcp.grafana
import bir_mcp.local
import bir_mcp.sql
from bir_mcp.config import SystemManagedConfig


class McpCategory(enum.StrEnum):
    gitlab = enum.auto()
    grafana = enum.auto()
    jira = enum.auto()
    local = enum.auto()


def build_mcp_server(
    enable_local_tools: Annotated[
        bool,
        typer.Option(
            help=inspect.cleandoc(
                """
                Whether to include local tools, such as those that interact with local 
                file system and perform local Git actions.
                """
            ),
        ),
    ] = False,
    include_non_readonly_tools: Annotated[
        bool,
        typer.Option(
            help=inspect.cleandoc(
                """
                Whether to include tools with ability to write and create new resources, 
                for example new Jira issues, GitLab branches or commits.
                """
            ),
        ),
    ] = False,
    include_destructive_tools: Annotated[
        bool,
        typer.Option(
            help=inspect.cleandoc(
                """
                Whether to include tools with ability to delete or overwrite resources,
                such as GitLab file updates.
                """
            ),
        ),
    ] = False,
    consul_host: Annotated[
        str | None,
        typer.Option(
            help=inspect.cleandoc(
                """
                The host of the Consul key-value store to load the system managed configuration from,
                with the SQL connections and default system connection credentials.
                Any parameters explicity provided to this function will override the ones 
                loaded from Consul.
                """
            ),
        ),
    ] = None,
    consul_key: Annotated[
        str | None,
        typer.Option(help="The key name of the Consul key-value store."),
    ] = None,
    consul_token: Annotated[
        str | None,
        typer.Option(help="The token to use for authentication with Consul."),
    ] = None,
    gitlab_private_token: Annotated[
        str | None,
        typer.Option(
            help=inspect.cleandoc(
                """
                The GitLab token to use for authentication with GitLab. To enable writing tools, 
                the token should have write API permissions.
                """
            ),
        ),
    ] = None,
    grafana_username: str | None = None,
    grafana_password: str | None = None,
    jira_token: str | None = None,
    gitlab_url: str = "https://gitlab.kapitalbank.az",
    grafana_url: str = "https://yuno.kapitalbank.az",
    jira_url: str = "https://jira-support.kapitalbank.az",
    timezone: Annotated[
        str,
        typer.Option(
            help=inspect.cleandoc(
                """
                The timezone to use for datetime formatting in the output of tools.
                """
            ),
        ),
    ] = "Asia/Baku",
    tools_max_output_length: Annotated[
        int | None,
        typer.Option(
            help=inspect.cleandoc(
                """
                The maximum output string length for tools, with longer strings being truncated. 
                Especially useful for AI clients with smaller context windows and those that 
                cannot automatically trim or summarize chat history, for example Claude Desktop.
                """
            )
        ),
    ] = None,
    verify_ssl: Annotated[bool, typer.Option(help="Whether to verify SSL certificates.")] = True,
    ca_file: Annotated[
        str | None,
        typer.Option(help="Path to a local certificate authority file to verify SSL certificates."),
    ] = None,
    prompts_to_tools: Annotated[
        bool,
        typer.Option(
            help=inspect.cleandoc(
                """
                Whether to convert prompts to tools. Not all MCP clients support prompts (for example 
                Windsurf at the time of writing), but all of them support tools.
                """
            )
        ),
    ] = False,
) -> fastmcp.FastMCP:
    ssl_verify = ca_file or verify_ssl  # Workaround because typer doesn't support union types.
    sql_contexts = []
    if consul_host and consul_key:
        config = SystemManagedConfig.from_consul(
            consul_host=consul_host,
            consul_token=consul_token,
            consul_key=consul_key,
        )
        gitlab_private_token = gitlab_private_token or config.gitlab_private_token
        grafana_username = grafana_username or config.grafana_username
        grafana_password = grafana_password or config.grafana_password
        jira_token = jira_token or config.jira_token
        gitlab_url = gitlab_url or config.gitlab_url
        grafana_url = grafana_url or config.grafana_url
        jira_url = jira_url or config.jira_url
        sql_contexts = config.sql_contexts

    server = fastmcp.FastMCP(
        name="Bir MCP server",
        instructions=inspect.cleandoc("""
            MCP server for BirBank.
        """),
    )
    common_params = dict(timezone=timezone)
    common_server_params = dict(
        include_non_readonly_tools=include_non_readonly_tools,
        include_destructive_tools=include_destructive_tools,
        max_output_length=tools_max_output_length,
        prompts_to_tools=prompts_to_tools,
    )
    if enable_local_tools:
        for local_mcp in [
            bir_mcp.local.Git(**common_params),
            bir_mcp.local.Filesystem(**common_params),
        ]:
            subserver = local_mcp.get_mcp_server(**common_server_params)
            server.mount(subserver, prefix=local_mcp.get_tag())

    for sql_context in sql_contexts:
        sql = bir_mcp.sql.SQL(sql_context=sql_context, **common_params)
        subserver = sql.get_mcp_server(**common_server_params)
        server.mount(subserver, prefix=sql.get_tag())

    common_params["ssl_verify"] = ssl_verify
    if gitlab_private_token:
        gitlab = bir_mcp.git_lab.GitLab(
            url=gitlab_url, private_token=gitlab_private_token, **common_params
        )
        subserver = gitlab.get_mcp_server(**common_server_params)
        server.mount(subserver, prefix=gitlab.get_tag())
    else:
        warnings.warn(
            "Since GitLab private token is not provided, the GitLab tools will not be available."
        )

    if grafana_username and grafana_password:
        grafana = bir_mcp.grafana.Grafana(
            url=grafana_url, auth=(grafana_username, grafana_password), **common_params
        )
        subserver = grafana.get_mcp_server(**common_server_params)
        server.mount(subserver, prefix=grafana.get_tag())
    else:
        warnings.warn(
            "Since Grafana username and password are not provided, the Grafana tools will not be available."
        )

    return server


@functools.wraps(build_mcp_server)
def build_and_run(*args, **kwargs):
    server = build_mcp_server(*args, **kwargs)
    server.run()


def main():
    typer.run(build_and_run)


if __name__ == "__main__":
    main()
