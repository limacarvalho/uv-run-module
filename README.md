# uv-run-module

A tiny launcher that **cd’s into your project** and runs **exactly the command you pass** via Astral `uv` (or `uvx`).  
Designed to be **Kubernetes argv-array friendly**: no quoting, no `--` injection, no reordering.
Compatible with jhsingle-native-proxy and jhub-app-proxy

## Why?

- K8s YAML `args` are split into tokens literally — quoting is a trap.
- You often need to run a tool from the project root (where `pyproject.toml` / `uv.lock` live).
- You want to keep your command **literal** (e.g., `flask run …`, `streamlit run …`, `uvicorn …`).

This module solves that:
- `chdir` into the project dir
- strip simple delimiters (`::`)
- lightly clean stray quotes
- **run exactly what you provide**

## Install

With [uv](https://docs.astral.sh/uv/):

```bash
uv pip install -e .
or
pip install -e .
```

## Usage (recommended form)

```bash
python -m uv_run_module PROJECT_DIR :: CMD [ARGS...]
```
•	PROJECT_DIR — directory with your app (typically holds pyproject.toml and/or uv.lock)
•	:: — optional delimiter; helps visually separate project path from the command
•	CMD [ARGS...] — your literal command tokens; no quotes required


## Examples

Flask
```bash
python -m uv_run_module /home/me/app :: flask run --host=0.0.0.0 --port=80
```

Streamlit
```bash
python -m uv_run_module /home/me/app :: streamlit run main.py --server.port=8892
```

Uvicorn
```bash
python -m uv_run_module /home/me/app :: uvicorn app:app --host 0.0.0.0 --port 8080
```

Gunicorn (with uvx)
```bash
UV_EXEC=uvx python -m uv_run_module /home/me/app :: gunicorn app:app -b 0.0.0.0:9000
```

Under the hood, the module runs either uv run <CMD ...> or uvx <CMD ...> depending on UV_EXEC.

### Kubernetes snippet

K8s args must be split into tokens — do not quote:

args:
  - python
  - -m
  - uv_run_module
  - /home/app
  - ::
  - streamlit
  - run
  - main.py
  - --server.port=8892

That produces (inside the container):
```bash
uv run streamlit run main.py --server.port=8892
```

Behavior & guarantees
  - Literal: your command order is preserved exactly.
  - No extras injected: we do not add -- or invent flags.
  - Delimiter cleanup: any :: tokens are removed before execution.
  - Quote cleanup: tokens like '"streamlit' or main.py" are cleaned.
  - Project-root execution: we cd into PROJECT_DIR before launching.

Legacy call (supported, but discouraged)

The module also accepts the old style:
```bash
python -m uv_run_module PORT PROJECT_DIR :: CMD [ARGS...]
```
  - PORT is detected and ignored (kept only for backward compatibility).
  - Prefer the project-first form going forward.

Environment variables
  - UV_EXEC — choose the runner:
  - default: uv
  - optional: uvx (alias for uv tool run)


## Troubleshooting
  - I see the delimiter in the command (e.g., ::).
Ensure you have the latest uv_run_module. The launcher strips every :: token.
  - No such file or directory for the command.
Make sure the tool is available in the environment (e.g., flask/streamlit/uvicorn installed).
Remember: the command is run via uv run or uvx, which resolves dependencies from the project (and/or user tool cache).
  - I want to force uvx.
Set UV_EXEC=uvx.
