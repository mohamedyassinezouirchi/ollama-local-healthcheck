# Ollama Local Healthcheck

**A tiny, read-only diagnostic CLI for your locally running Ollama server.**

[![Python tests](https://github.com/mohamedyassinezouirchi/ollama-local-healthcheck/actions/workflows/ci.yml/badge.svg)](https://github.com/mohamedyassinezouirchi/ollama-local-healthcheck/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
[![MIT license](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

When local AI isn't working, the first question is simple: **is Ollama reachable, and which models are actually installed?** This lightweight utility answers both questions using Ollama's local HTTP API.

No cloud account. No API key. No third-party Python packages.

> **Status:** Small, working MVP intended for localhost diagnostics—not a full monitoring system or model benchmark.

## Features

- Checks whether Ollama responds on a **loopback-only** HTTP address.
- Reads its reported version using `/api/version`.
- Lists locally installed model names using `/api/tags`.
- Provides readable terminal output or machine-readable JSON (`--json`).
- Uses configurable per-request timeouts.
- Returns exit code **0** on success and **1** on connection or validation errors.
- Rejects non-local hosts, non-HTTP schemes, unexpected paths, and HTTP redirects.

## Requirements

- Python **3.10+**
- Ollama installed if you want to test a real local server
- No additional Python packages

## Quick start

```bash
git clone https://github.com/mohamedyassinezouirchi/ollama-local-healthcheck.git
cd ollama-local-healthcheck
python healthcheck.py
```

If Ollama isn't running yet, start it in another terminal:

```bash
ollama serve
```

Default endpoint: `http://127.0.0.1:11434`.

### Example output

```text
Ollama is reachable at http://127.0.0.1:11434
Version: 0.x.x
Installed models: 2
  - gemma3:latest
  - llama3.2:latest
```

This is **illustrative output**, not a measured result from your machine. Actual version and model names depend on your installation.

### JSON output

```bash
python healthcheck.py --json
```

Example:

```json
{
  "healthy": true,
  "endpoint": "http://127.0.0.1:11434",
  "version": "0.x.x",
  "model_count": 2,
  "models": ["gemma3:latest", "llama3.2:latest"]
}
```

### Custom loopback port

```bash
python healthcheck.py --url http://localhost:11434 --timeout 5
```

The tool intentionally does **not** connect to LAN, internet, or remote Ollama endpoints.

## Command options

| Option | Description |
| --- | --- |
| `--url URL` | Ollama **loopback-only** origin; default `http://127.0.0.1:11434` |
| `--timeout SECONDS` | Per-request timeout; greater than 0 and at most 60 |
| `--json` | Emit JSON for terminal scripts and tools |
| `--help` | Show CLI usage |

For errors, the command exits with code `1` and prints a message; `--json` includes `"healthy": false` and an `error` field.

## How it works

1. Validates that the endpoint is an HTTP **loopback** origin with an explicit port.
2. Sends a read-only `GET /api/version` request.
3. Sends a read-only `GET /api/tags` request.
4. Extracts model names, displays the result, and returns a status code.

It **does not** invoke models, download weights, run benchmarks, change configuration, or send model data to a remote service.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The included tests use mocks and do not require Ollama to be installed. GitHub Actions runs tests for Python 3.10 and 3.12.

## Project layout

```text
ollama-local-healthcheck/
├── healthcheck.py
├── tests/
│   └── test_healthcheck.py
├── .github/workflows/
│   └── ci.yml
├── .gitignore
├── LICENSE
└── README.md
```

## Limitations

- This is a **one-time check**, not continuous uptime monitoring.
- It doesn't assess model accuracy, speed, memory usage, or generation readiness.
- A reachable Ollama API does not guarantee that any specific model can execute successfully.
- For safety and simplicity, only local loopback addresses are supported.
- Responses are capped at 1 MiB; extremely large model lists may exceed this limit.

## Roadmap

Potential next steps: a safe local dashboard, optional checks for running models, richer error messages, and exportable health summaries. These features are **not yet implemented**.

## Contributions

Issues, reproducible test cases, small fixes, and documentation improvements are welcome. Please do not post credentials or confidential model inputs in issues.

## Author

**Mohamed Yassine Zouirchi** · [GitHub](https://github.com/mohamedyassinezouirchi)

## License

Released under the [MIT License](LICENSE).

_Ollama is a separate project; this utility is not affiliated with its maintainers._
