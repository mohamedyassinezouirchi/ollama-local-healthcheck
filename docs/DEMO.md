# Demo: Local Ollama diagnostics

A short, reproducible way to show what this repository currently does.

## Walkthrough

Start a locally installed Ollama server with `ollama serve` (in a separate terminal), then run `python healthcheck.py`. Try `python healthcheck.py --json` to get structured results. If Ollama is not installed, the tool prints a connection error.

## Suggested content for a public demo

- Show your terminal with the command and actual output.
- Explain the developer problem in one sentence.
- Share the repository link and the specific limitation below.
- Invite practical feedback or a reproducible issue instead of asking for stars.

## Honest limitations

Only loopback HTTP origins are accepted. Do not use screenshots containing private model names if they are sensitive.

## Validation

Run the project's tests where applicable:

```bash
python -m unittest discover -s tests -v
```

Avoid presenting a demo output as a real performance measurement unless you actually collected it.
