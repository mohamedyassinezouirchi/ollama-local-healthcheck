#!/usr/bin/env python3
"""Read-only health checks for a locally running Ollama server."""
import argparse
import ipaddress
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

DEFAULT_URL = "http://127.0.0.1:11434"


def validate_base_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "http" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only plain HTTP loopback URLs are allowed")
    try:
        is_loopback = ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError:
        is_loopback = parsed.hostname.lower() == "localhost"
    if not is_loopback or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("Provide a loopback origin only, e.g. http://127.0.0.1:11434")
    if parsed.port is None or not 1 <= parsed.port <= 65535:
        raise ValueError("An explicit valid port is required")
    return url.rstrip("/")


def get_json(url: str, timeout: float = 3.0) -> dict:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    # Prevent following redirects away from localhost.
    from urllib.request import build_opener, HTTPRedirectHandler
    class NoRedirects(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    with build_opener(NoRedirects).open(request, timeout=timeout) as response:
        data = response.read(1024 * 1024 + 1)
        if len(data) > 1024 * 1024:
            raise ValueError("Ollama response exceeds 1 MiB")
        obj = json.loads(data.decode("utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("Unexpected API response shape")
        return obj


def check(base_url: str, timeout: float = 3.0) -> dict:
    base_url = validate_base_url(base_url)
    version_data = get_json(base_url + "/api/version", timeout)
    tag_data = get_json(base_url + "/api/tags", timeout)
    models = tag_data.get("models", [])
    if not isinstance(models, list):
        raise ValueError("Unexpected models response")
    names = [item["name"] for item in models
             if isinstance(item, dict) and isinstance(item.get("name"), str)]
    return {"healthy": True, "endpoint": base_url,
            "version": version_data.get("version", "unknown"),
            "model_count": len(names), "models": names}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only localhost Ollama health check")
    parser.add_argument("--url", default=DEFAULT_URL, help="Ollama local origin (default: %(default)s)")
    parser.add_argument("--timeout", type=float, default=3, help="Per-request timeout seconds")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args(argv)
    if not 0 < args.timeout <= 60:
        parser.error("--timeout must be between 0 and 60 seconds")
    try:
        result = check(args.url, args.timeout)
    except (ValueError, OSError, URLError, HTTPError, json.JSONDecodeError) as exc:
        error = {"healthy": False, "endpoint": args.url, "error": str(exc)}
        if args.json:
            print(json.dumps(error, ensure_ascii=False))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
            print("Is Ollama running locally? Try: ollama serve", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Ollama is reachable at {result['endpoint']}")
        print(f"Version: {result['version']}")
        print(f"Installed models: {result['model_count']}")
        for model in result["models"]:
            print(f"  - {model}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
