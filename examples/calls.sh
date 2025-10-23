#!/usr/bin/env bash
set -euxo pipefail

# Flask
python -m uv_run_module /path/to/app :: flask run --host=0.0.0.0 --port=80

# Streamlit
python -m uv_run_module /path/to/app :: streamlit run main.py --server.port=8892

# Uvicorn
python -m uv_run_module /path/to/app :: uvicorn app:app --host 0.0.0.0 --port 8080

# Force uvx instead of uv
UV_EXEC=uvx python -m uv_run_module /path/to/app :: gunicorn app:app -b 0.0.0.0:9000