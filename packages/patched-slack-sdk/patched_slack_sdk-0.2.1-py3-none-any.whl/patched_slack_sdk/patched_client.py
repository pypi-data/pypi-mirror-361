from typing import Optional, List
from ssl import SSLContext

from slack_sdk import WebClient
from slack_sdk.web.base_client import BaseClient
from slack_sdk.http_retry.handler import RetryHandler
import logging

from patched_slack_sdk.local_storage import SlackLocalStorage


class BasePatchedClient(BaseClient):
    BASE_URL = "https://www.slack.com/api/"

    def __init__(
        self,
        token: Optional[str] = None,
        workspace_name: Optional[str] = None,
        base_url: str = BASE_URL,
        timeout: int = 30,
        ssl: Optional[SSLContext] = None,
        proxy: Optional[str] = None,
        headers: Optional[dict] = None,
        user_agent_prefix: Optional[str] = None,
        user_agent_suffix: Optional[str] = None,
        # for Org-Wide App installation
        team_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        retry_handlers: Optional[List[RetryHandler]] = None,
    ) -> None:
        if token is None:
            workspace_tokens = SlackLocalStorage.get_workspace_tokens()
            if len(workspace_tokens) == 1:
                token = workspace_tokens[0].token
            elif workspace_name is not None:
                workspace = next(
                    (t for t in workspace_tokens if t.name == workspace_name), None
                )
                if workspace is not None:
                    token = workspace.token
                else:
                    raise ValueError(
                        f"Workspace {workspace_name} is not found in the local storage.\n"
                        f"Available options: {', '.join(t.name for t in workspace_tokens)}"
                    )
            else:
                raise ValueError(
                    "The token is not given and there are multiple workspaces in the local storage.\n"
                    "Please specify the workspace name using the workspace_name parameter.\n"
                    f"Available options: {', '.join(t.name for t in workspace_tokens)}"
                )
        if headers is None:
            headers = {
                'cookie': f'd={SlackLocalStorage.get_access_token()};'
            }
        elif 'cookie' not in headers:
            headers['cookie'] = f'd={SlackLocalStorage.get_access_token()};'
        elif headers['cookie'].find('d=') == -1:
            headers['cookie'] += f'd={SlackLocalStorage.get_access_token()};'
        super().__init__(
            token=token,
            base_url=base_url,
            timeout=timeout,
            ssl=ssl,
            proxy=proxy,
            headers=headers,
            user_agent_prefix=user_agent_prefix,
            user_agent_suffix=user_agent_suffix,
            team_id=team_id,
            logger=logger,
            retry_handlers=retry_handlers,
        )


class PatchedWebClient(BasePatchedClient, WebClient):
    pass
