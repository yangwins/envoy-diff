# envoy-diff

> Diff environment variable sets across staging and production deployments.

---

## Installation

```bash
pip install envoy-diff
```

Or install from source:

```bash
git clone https://github.com/yourorg/envoy-diff.git && cd envoy-diff && pip install .
```

---

## Usage

Compare environment variables between two deployments:

```bash
envoy-diff --source staging --target production
```

You can also point directly at `.env` files or export outputs:

```bash
envoy-diff --file staging.env --file production.env

# Output only keys that differ
envoy-diff --source staging --target production --only-diff

# Export results as JSON
envoy-diff --source staging --target production --format json > diff.json
```

**Example output:**

```
KEY                  STAGING              PRODUCTION
---                  -------              ----------
API_TIMEOUT          30                   60
LOG_LEVEL            debug                warn
NEW_RELIC_KEY        (not set)            abc123xyz
FEATURE_FLAG_X       true                 (not set)
```

---

## Configuration

Set credentials or endpoints via environment variables or a config file:

```bash
export ENVOY_DIFF_TOKEN=your_api_token
export ENVOY_DIFF_HOST=https://your-deployment-api.example.com
```

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

---

## License

[MIT](LICENSE)