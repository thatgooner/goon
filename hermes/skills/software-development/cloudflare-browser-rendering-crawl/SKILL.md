---
name: cloudflare-browser-rendering-crawl
description: Use Cloudflare Browser Rendering /crawl endpoint to crawl an entire site from a starting URL.
triggers:
  - Cloudflare Browser Rendering crawl endpoint
  - crawl an entire site with Cloudflare
  - /browser-rendering/crawl API
---

# Cloudflare Browser Rendering /crawl endpoint

Use this when you need to kick off a site crawl through Cloudflare Browser Rendering.

## What it does
Sends a POST request to Cloudflare's Browser Rendering crawl endpoint with a starting URL.
According to Cloudflare's official changelog, the endpoint can automatically discover, render, and return content from an entire website as HTML, Markdown, or structured JSON.

Endpoint pattern:
`https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-rendering/crawl`

Auth:
- Bearer API token in `Authorization` header
- `Content-Type: application/json`

## Basic request

```bash
curl -X POST 'https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-rendering/crawl' \
  -H 'Authorization: Bearer <apiToken>' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com/"
  }'
```

## Working example

```bash
curl -X POST 'https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/browser-rendering/crawl' \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://blog.cloudflare.com/"}'
```

## When to use
- JS-heavy sites where browser-based crawling is preferable
- Site discovery / content collection workflows
- Browser Rendering automation pipelines

## Checklist
1. Confirm Cloudflare account has Browser Rendering enabled.
2. Confirm API token has required permissions.
3. Provide full starting URL in the JSON body.
4. Inspect the API response for crawl/job metadata.
5. If behavior changed since announcement, check current Cloudflare docs before building around it.

## Notes
- This skill was captured from a Cloudflare Developers announcement showing the endpoint and request shape.
- If the endpoint returns auth or feature errors, verify account access and current docs first.
