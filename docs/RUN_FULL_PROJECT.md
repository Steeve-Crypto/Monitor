# Run Monitor Full Local Project

This project is local-first. It does not generate fake leads. Unconfigured sources fail with 503 until you configure real integrations.

## 1. Backend API

Open a terminal:

```bash
cd "/mnt/c/Users/12404/Downloads/Quant I/Monitor/apps/api"
export MONITOR_SIGNAL_MESH_STORE_PATH="/mnt/c/Users/12404/Downloads/Quant I/Monitor/.monitor/signal_mesh_store.json"
export MONITOR_PROFILE_VAULT_PATH="/mnt/c/Users/12404/Downloads/Quant I/Monitor/.monitor/profile_vault.json"
# Optional real source:
# export MONITOR_CRYPTO_RSS_FEED_URL="https://example.com/jobs.rss"
# Optional real executor webhook for approved external sends/submissions:
# export MONITOR_EXECUTOR_WEBHOOK_URL="https://your-real-executor.example.com/submit"
uv run uvicorn monitor_api.app:app --host 127.0.0.1 --port 8765 --reload
```

Health check:

```bash
curl http://127.0.0.1:8765/api/health
```

## 2. Desktop command deck

Open a second terminal:

```bash
cd "/mnt/c/Users/12404/Downloads/Quant I/Monitor/apps/desktop"
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

The Vite dev proxy sends `/api/*` requests to `http://127.0.0.1:8765`.

## 3. Configure a real ingestion source

Currently usable live source:

- `crypto_rss`

Set:

```bash
export MONITOR_CRYPTO_RSS_FEED_URL="https://REAL_PUBLIC_RSS_URL"
```

Then run from the UI or with curl:

```bash
curl -X POST http://127.0.0.1:8765/api/scans/crypto_rss/run \
  -H 'Content-Type: application/json' \
  -d '{"query":"python web3 automation dashboard","limit":10}'
```

Unconfigured sources such as `x`, `discord`, `marketplaces`, and generic `crypto` intentionally return 503 until real credentials/adapters are implemented.

## 4. Feedback loop workflow

Use this loop after each implementation phase:

```bash
cd "/mnt/c/Users/12404/Downloads/Quant I/Monitor/apps/api"
uv run pytest -q && uv run ruff check .

cd "/mnt/c/Users/12404/Downloads/Quant I/Monitor/apps/desktop"
npm run test && npm run check && npm run build

cd "/mnt/c/Users/12404/Downloads/Quant I/Monitor"
git status --short
git add .
git commit -m "feat: describe verified phase"
git push origin main
```

If push fails with GitHub auth, run one of:

```bash
gh auth login
```

or configure SSH/token auth for `https://github.com/Steeve-Crypto/Monitor.git`.

## 5. Approval/execution flow

External sends/submissions require:

1. A real opportunity.
2. A draft/action proposal.
3. Approval.
4. A configured real executor adapter.

Without a configured executor, execution returns 503 and does not pretend to send.

Manual API sequence:

```bash
# Create draft
curl -X POST http://127.0.0.1:8765/api/opportunities/OPPORTUNITY_ID/draft \
  -H 'Content-Type: application/json' \
  -d '{}'

# Propose action
curl -X POST http://127.0.0.1:8765/api/opportunities/OPPORTUNITY_ID/actions/propose \
  -H 'Content-Type: application/json' \
  -d '{}'

# Approve action
curl -X POST http://127.0.0.1:8765/api/actions/ACTION_ID/approve \
  -H 'Content-Type: application/json' \
  -d '{"decided_by":"operator"}'

# Execute approved action through configured real executor
curl -X POST http://127.0.0.1:8765/api/actions/ACTION_ID/execute
```

## 6. Inspect logs/state

```bash
curl http://127.0.0.1:8765/api/store/stats
curl http://127.0.0.1:8765/api/signals
curl http://127.0.0.1:8765/api/opportunities
curl http://127.0.0.1:8765/api/actions/proposals
curl http://127.0.0.1:8765/api/applications
curl http://127.0.0.1:8765/api/audit
```
