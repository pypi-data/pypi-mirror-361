# Patched slack-sdk
__This project is not endorsed or authorised in any way by Slack Technologies LLC.__

The Slack API is essential for all Slack clients, such as the official desktop app and third-party bots, to interact with and modify the data that shapes the Slack user experience. Authorization is required from all clients to access this API.

Since July 2021, individual user access to the Slack API (excluding bot access) has been granted through a personal token (starting with xoxc-) and a cookie named d. Each Slack Workspace has its unique personal token, while the cookie remains the same across all workspaces.

If you are using the Slack desktop app, these credentials are stored locally on your machine. This modified client extracts them from the app's local storage, allowing their use for purposes beyond those supported by the app itself.

## QuickStart

### Requirements

- Python <=3.8 - because leveldb is not compatible with a higher version

### Installation

```bash
pip install patched-slack
```

## Usage

Authentication test

```python
from patched_slack_sdk import PatchedWebClient

client = PatchedWebClient()
print(client.auth_test())
```

Update slack status

```python
from patched_slack_sdk import PatchedWebClient

client = PatchedWebClient()
client.users_profile_set(
    profile={
        "status_text": "I'm out of the office",
        "status_emoji": ":palm_tree:",
    }
)
```

## Contributing
Contributions are always welcome! Please feel free to submit a pull request.