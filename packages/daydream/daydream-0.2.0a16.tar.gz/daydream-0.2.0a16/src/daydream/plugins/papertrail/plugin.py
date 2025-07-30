import os

import questionary
from pydantic import AwareDatetime, BaseModel

from daydream.config.utils import Config, PluginSettings
from daydream.plugins.base import Plugin
from daydream.plugins.mixins import McpServerMixin, tool
from daydream.plugins.papertrail.client import PapertrailClient, PapertrailLogEvent

CLAUDE_DESKTOP_RESULT_MAX_LENGTH = 1048576
RESULT_LIMIT = int(CLAUDE_DESKTOP_RESULT_MAX_LENGTH * 0.9)


class PapertrailSearchResult(BaseModel):
    """Result of a Papertrail log search."""

    """Number of logs that were found, before any truncation"""
    count: int
    """True when the search results were truncated due to the response size limit (count is not changed when this happens)"""
    truncated: bool = False
    """The log events that were found"""
    results: list[PapertrailLogEvent]


class PapertrailPlugin(Plugin, McpServerMixin):
    _client: PapertrailClient

    def init_plugin(self) -> None:
        super().init_plugin()
        self._client = PapertrailClient(
            token=self._settings.get("token")
            or os.environ.get("PAPERTRAIL_TOKEN", "")
            or os.environ.get("PAPERTRAIL_API_TOKEN", ""),
        )

    async def validate_plugin_config(self) -> None:
        await super().validate_plugin_config()
        await self._client.verify_connection()

    async def interactive_configure(self, cfg: Config) -> PluginSettings:
        """Interactive wizard for configuring the settings of this plugin."""
        existing_token = os.environ.get("PAPERTRAIL_TOKEN")
        if existing_token is not None:
            return {
                "token": await questionary.text(
                    "Enter your Papertrail API token (default from PAPERTRAIL_TOKEN env var)",
                    default=existing_token,
                ).unsafe_ask_async(),
            }
        return {
            "token": await questionary.text(
                "Enter your Papertrail API token",
            ).unsafe_ask_async(),
        }

    @tool()
    async def search_logs(
        self,
        query: str,
        min_time: AwareDatetime,
        max_time: AwareDatetime,
    ) -> PapertrailSearchResult:
        """Search Papertrail for logs within a given time range

        Args:
            query (str): The search query.
            min_time (AwareDatetime): The starting time for the range within which to search.
            max_time (AwareDatetime): The ending time for the range within which to search.

        Returns:
            PapertrailSearchResult: logs that matched the query and fit within response limit
        """
        logs = sorted(
            [
                log
                async for log in self._client.search(
                    query=query,
                    min_time=min_time,
                    max_time=max_time,
                )
            ],
            key=lambda x: x.received_at,
        )
        result = PapertrailSearchResult(results=logs, count=len(logs))
        content_length = len(result.model_dump_json(indent=2))
        if content_length <= RESULT_LIMIT:
            return result
        result.truncated = True
        while result.results and content_length > RESULT_LIMIT:
            result.results.pop()
            content_length = len(result.model_dump_json(indent=2))
        return result
