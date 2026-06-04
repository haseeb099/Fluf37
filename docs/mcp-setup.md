# Cursor MCP setup (Nexus AI)

Project MCP config: [.cursor/mcp.json](../.cursor/mcp.json).

| Server | Purpose | Required env (user / OS) |
|--------|---------|---------------------------|
| **chrome-devtools** | Network, WebSocket, performance on local dashboard | None |
| **github** | Issues, PRs, CI, repo search | `GITHUB_TOKEN` — fine-grained PAT with `repo` (+ `workflow` read if you inspect Actions) |
| **context7** | Up-to-date FastAPI, Next.js, Pydantic, Chroma, etc. docs | None (works without a key). Optional: add `CONTEXT7_API_KEY` to the server `env` in `mcp.json` via [context7.com/dashboard](https://context7.com/dashboard) for higher rate limits |

## One-time setup (Windows)

Set tokens in your user environment (not in `.env` — the Nexus app does not read these):

```powershell
# GitHub: https://github.com/settings/tokens
[System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "ghp_...", "User")

```

Optional Context7 API key — add to `.cursor/mcp.json` under `context7`:

```json
"env": { "CONTEXT7_API_KEY": "${env:CONTEXT7_API_KEY}" }
```

Then set `[System.Environment]::SetEnvironmentVariable("CONTEXT7_API_KEY", "ctx7_...", "User")`.

Restart Cursor after changing env vars or `mcp.json`.

## Verify in Cursor

1. **Settings → Tools & MCP** — all three servers should show connected (green).
2. Ask the agent to use Context7 for `fastapi` WebSocket patterns or to list open issues on this repo (GitHub MCP).

## Security

- Do not commit PATs or Context7 keys into `mcp.json` or the repo.
- Use a PAT scoped to this repository only when possible.
