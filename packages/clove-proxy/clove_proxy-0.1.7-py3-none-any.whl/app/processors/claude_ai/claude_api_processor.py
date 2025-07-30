from app.core.http_client import (
    Response,
    AsyncSession,
    create_session,
)
from datetime import datetime, timedelta, UTC
from typing import Dict
from loguru import logger
from fastapi.responses import StreamingResponse

from app.models.claude import TextContent
from app.processors.base import BaseProcessor
from app.processors.claude_ai import ClaudeAIContext
from app.services.account import account_manager
from app.core.exceptions import (
    ClaudeHttpError,
    ClaudeRateLimitedError,
    InvalidModelNameError,
    NoAccountsAvailableError,
)
from app.core.config import settings


class ClaudeAPIProcessor(BaseProcessor):
    """Processor that calls Claude Messages API directly using OAuth authentication."""

    def __init__(self):
        self.messages_api_url = (
            settings.claude_api_baseurl.encoded_string() + "/v1/messages"
        )

    async def _request_messages_api(
        self, session: AsyncSession, request_json: str, headers: Dict[str, str]
    ) -> Response:
        """Make HTTP request with retry mechanism for curl_cffi exceptions."""
        response: Response = await session.request(
            "POST",
            self.messages_api_url,
            data=request_json,
            headers=headers,
            stream=True,
        )
        return response

    async def process(self, context: ClaudeAIContext) -> ClaudeAIContext:
        """
        Process Claude API request using OAuth authentication.

        Requires:
            - messages_api_request in context

        Produces:
            - response in context (StreamingResponse)
        """
        if context.response:
            logger.debug("Skipping ClaudeAPIProcessor due to existing response")
            return context

        if not context.messages_api_request:
            logger.warning(
                "Skipping ClaudeAPIProcessor due to missing messages_api_request"
            )
            return context

        try:
            account = await account_manager.get_account_for_oauth(
                is_max=True
                if (context.messages_api_request.model in settings.max_models)
                else None
            )

            with account:
                request_json = self._prepare_request_json(context)
                headers = self._prepare_headers(account.oauth_token.access_token)

                session = create_session(
                    proxy=settings.proxy_url,
                    timeout=settings.request_timeout,
                    impersonate="chrome",
                    follow_redirects=False,
                )

                response = await self._request_messages_api(
                    session, request_json, headers
                )

                # Handle rate limiting
                if response.status_code == 429:
                    now = datetime.now(UTC)
                    next_hour = now.replace(
                        minute=0, second=0, microsecond=0
                    ) + timedelta(hours=1)
                    logger.warning(f"Rate limited by Claude API, resets at {next_hour}")
                    raise ClaudeRateLimitedError(resets_at=next_hour)

                if response.status_code >= 400:
                    error_data = await response.ajson()

                    if (
                        response.status_code == 400
                        and error_data.get("error", {}).get("message")
                        == "system: Invalid model name"
                    ):
                        raise InvalidModelNameError(context.messages_api_request.model)

                    logger.error(
                        f"Claude API error: {response.status_code} - {error_data}"
                    )
                    raise ClaudeHttpError(
                        url=self.messages_api_url,
                        status_code=response.status_code,
                        error_type=error_data.get("error", {}).get("type", "unknown"),
                        error_message=error_data.get("error", {}).get(
                            "message", "Unknown error"
                        ),
                    )

                async def stream_response():
                    async for chunk in response.aiter_bytes():
                        yield chunk

                    await session.close()

                filtered_headers = {}
                for key, value in response.headers.items():
                    if key.lower() in ["content-encoding", "content-length"]:
                        logger.debug(f"Filtering out header: {key}: {value}")
                        continue
                    filtered_headers[key] = value

                context.response = StreamingResponse(
                    stream_response(),
                    status_code=response.status_code,
                    headers=filtered_headers,
                )

                # Stop pipeline on success
                context.metadata["stop_pipeline"] = True
                logger.info("Successfully processed request via Claude API")

        except (NoAccountsAvailableError, InvalidModelNameError):
            logger.debug("No accounts available for Claude API, continuing pipeline")

        return context

    def _prepare_request_json(self, context: ClaudeAIContext) -> str:
        """Prepare request json with system message injection."""
        request = context.messages_api_request

        # Handle system field
        system_message = TextContent(
            type="text",
            text=settings.custom_prompt
            or "You are Claude Code, Anthropic's official CLI for Claude.",
        )

        if isinstance(request.system, str):
            request.system = [system_message, TextContent(text=request.system)]
        elif isinstance(request.system, list):
            request.system = [system_message] + request.system
        else:
            request.system = [system_message]

        return request.model_dump_json(exclude_none=True)

    def _prepare_headers(self, access_token: str) -> Dict[str, str]:
        """Prepare headers for Claude API request."""
        return {
            "Authorization": f"Bearer {access_token}",
            "anthropic-beta": "oauth-2025-04-20",
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
