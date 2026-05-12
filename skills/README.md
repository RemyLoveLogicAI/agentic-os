# Skills Catalog

Skills are MCP server integrations wired into agent workspaces via the tool bus.
Each entry maps to a `VoltAgent/awesome-agent-skills` compatible server.

## Monetization

| Skill | Server | Purpose |
|---|---|---|
| x402 USDC Billing | `coinbase/monetize-service` | Per-request USDC billing on Base chain; no Stripe needed |

## Browser & Scraping

| Skill | Server | Purpose |
|---|---|---|
| Firecrawl | `firecrawl/firecrawl-build-interact` | Multi-step browser flows: login, scrape, paginate |
| Browserbase | `browserbase/browser` | Remote isolated cloud browser; no local Chromium |
| Playwright | `openai/playwright` | Navigation, form fill, data extraction |

## Distribution

| Skill | Server | Purpose |
|---|---|---|
| Typefully | `typefully/typefully` | Schedule posts to X, LinkedIn, Threads, Bluesky, Mastodon |

## AI Generation

| Skill | Server | Purpose |
|---|---|---|
| fal Video Edit | `fal-ai-community/fal-video-edit` | Restyle, upscale, remove background, add audio |
| fal Audio | `fal-ai-community/fal-audio` | Text-to-speech and speech-to-text |
| Venice Music | `veniceai/venice-audio-music` | Autonomous music generation and retrieval |
| Replicate | `replicate/replicate` | Run any AI model — image, video, audio |

## Infrastructure

| Skill | Server | Purpose |
|---|---|---|
| Cloudflare Agents | `cloudflare/agents-sdk` | Stateful agents with scheduling and RPC on Workers |
| Sentry AI | `getsentry/sentry-setup-ai-monitoring` | Monitor OpenAI/Anthropic/LangChain calls in production |

## Usage

Add any skill to a workspace by listing its server name in `workspace.json`:

```json
{
  "tools": ["typefully/typefully", "coinbase/monetize-service"],
  "apps": [
    {
      "name": "typefully",
      "type": "mcp",
      "server": "typefully/typefully"
    }
  ]
}
```

See individual `workspace.json` files in `agents/` for working examples.
