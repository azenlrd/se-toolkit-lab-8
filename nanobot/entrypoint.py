#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add the venv site-packages to sys.path
venv_site_packages = Path("/opt/nanobot-venv/lib/python3.14/site-packages")
if venv_site_packages.exists() and str(venv_site_packages) not in sys.path:
    sys.path.insert(0, str(venv_site_packages))


def main():
    config_path = Path("/app/nanobot/config.json")
    workspace_dir = Path("/app/nanobot/workspace")
    resolved_path = Path(tempfile.gettempdir()) / "config.resolved.json"

    with open(config_path, "r") as f:
        config = json.load(f)

    # Override provider settings from env vars
    if "LLM_API_KEY" in os.environ:
        config["providers"]["custom"]["apiKey"] = os.environ["LLM_API_KEY"]
    if "LLM_API_BASE_URL" in os.environ:
        config["providers"]["custom"]["apiBase"] = os.environ["LLM_API_BASE_URL"]
    if "LLM_API_MODEL" in os.environ:
        config["agents"]["defaults"]["model"] = os.environ["LLM_API_MODEL"]

    # Override gateway settings
    if "NANOBOT_GATEWAY_CONTAINER_ADDRESS" in os.environ:
        config["gateway"]["host"] = os.environ["NANOBOT_GATEWAY_CONTAINER_ADDRESS"]
    if "NANOBOT_GATEWAY_CONTAINER_PORT" in os.environ:
        config["gateway"]["port"] = int(os.environ["NANOBOT_GATEWAY_CONTAINER_PORT"])

    # Override LMS MCP server settings
    if "NANOBOT_LMS_BACKEND_URL" in os.environ:
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = os.environ["NANOBOT_LMS_BACKEND_URL"]
    if "NANOBOT_LMS_API_KEY" in os.environ:
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = os.environ["NANOBOT_LMS_API_KEY"]

    # Enable and configure webchat channel
    if "NANOBOT_WEBCHAT_CONTAINER_ADDRESS" in os.environ:
        config["channels"]["webchat"] = {
            "enabled": True,
            "host": os.environ["NANOBOT_WEBCHAT_CONTAINER_ADDRESS"],
            "port": int(os.environ["NANOBOT_WEBCHAT_CONTAINER_PORT"]),
            "allowFrom": ["*"],
        }
    if "NANOBOT_ACCESS_KEY" in os.environ:
        if "webchat" not in config["channels"]:
            config["channels"]["webchat"] = {"enabled": True, "allowFrom": ["*"]}
        config["channels"]["webchat"]["accessKey"] = os.environ["NANOBOT_ACCESS_KEY"]

    # Configure mcp_webchat MCP server
    if "NANOBOT_WEBCHAT_UI_RELAY_URL" in os.environ and "NANOBOT_WEBCHAT_UI_TOKEN" in os.environ:
        config["tools"]["mcpServers"]["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {
                "NANOBOT_WEBCHAT_UI_RELAY_URL": os.environ["NANOBOT_WEBCHAT_UI_RELAY_URL"],
                "NANOBOT_WEBCHAT_UI_TOKEN": os.environ["NANOBOT_WEBCHAT_UI_TOKEN"],
            }
        }

    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}", file=sys.stderr)

    # Launch nanobot gateway using sys.argv
    import sys as _sys
    _sys.argv = ["nanobot", "gateway", "--config", str(resolved_path), "--workspace", str(workspace_dir)]
    
    from nanobot.cli.commands import app
    app()


if __name__ == "__main__":
    main()
