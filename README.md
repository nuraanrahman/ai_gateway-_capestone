# AI Gateway

A unified API gateway that lets you talk to OpenAI and Anthropic models through a single endpoint. Built with FastAPI, deployed on Render.

**Live demo:** [ai-gateway-capestone.onrender.com/docs](https://ai-gateway-capestone.onrender.com/docs#/)

---

## What it does

Instead of integrating directly with each LLM provider, you send requests to this gateway. It handles auth, routes to the right model, tracks token usage, and returns a consistent response shape — regardless of which provider is behind it.

**Core features:**

- **Multi-provider routing** — supports OpenAI (`gpt-4o`, `gpt-4o-mini`) and Anthropic (`claude-sonnet-4-6`, `claude-haiku-4-5`) out of the box
- **JWT auth + API keys** — register, log in, mint API keys, revoke them
- **Streaming** — real-time token streaming via Server-Sent Events
- **Session memory** — pass a `session_id` and the gateway maintains conversation history across requests
- **Structured extraction** — send a JSON schema, get back structured data (powered by Instructor)
- **Cost estimation** — every response includes an `estimated_cost_usd` field based on token usage

---

## API overview

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | — | Create an account |
| POST | `/auth/login` | — | Get a JWT token |
| POST | `/auth/keys` | JWT | Mint an API key |
| GET | `/auth/keys` | JWT | List your API keys |
| DELETE | `/auth/keys/{id}` | JWT | Revoke a key |
| GET | `/providers` | API key | List available models |
| POST | `/v1/chat` | API key | Chat completion (streaming supported) |
| POST | `/v1/extract` | API key | Structured data extraction |
| DELETE | `/v1/sessions/{id}` | API key | Clear a session's history |

Full interactive docs at `/docs`.

---

## Running locally

```bash
git clone https://github.com/nuraanrahman/ai_gateway-_capestone.git
cd ai_gateway-_capestone
cp .env.example .env   # fill in your API keys
docker compose up
```

The API will be available at `http://localhost:8000`.

**Required env vars:**

```
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
JWT_SECRET=          # any long random string
ADMIN_TOKEN=         # optional, for admin routes
```

---

## Quick start

**1. Register and get a token**
```bash
curl -X POST https://ai-gateway-capestone.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

curl -X POST https://ai-gateway-capestone.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'
```

**2. Mint an API key**
```bash
curl -X POST https://ai-gateway-capestone.onrender.com/auth/keys \
  -H "Authorization: Bearer <your_jwt>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-key"}'
```

**3. Chat**
```bash
curl -X POST https://ai-gateway-capestone.onrender.com/v1/chat \
  -H "X-API-Key: <your_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Tech stack

- **FastAPI** — async Python web framework
- **Pydantic v2** — request/response validation
- **python-jose** — JWT handling
- **Instructor** — structured LLM output
- **Docker** — containerized for consistent deploys
- **Render** — hosting

---

## Project structure

```
app/
├── core/          # config, logging, auth, in-memory store
├── middleware/    # request ID injection
├── models/        # request/response schemas
├── providers/     # OpenAI + Anthropic adapters, registry
├── routers/       # auth, chat, providers
└── services/      # session memory, cost estimation
```
