from __future__ import annotations
import os, sys, shutil, subprocess, logging
from typing import List, Optional

log = logging.getLogger("uv_run_module")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DELIMS = {"::"}  # strip these delimiter tokens anywhere in the argv list

def _which(name: str) -> Optional[str]:
    return shutil.which(name)

def _is_int(s: str) -> bool:
    try:
        int(s); return True
    except Exception:
        return False

def _clean_token(tok: str) -> str:
    """Remove surrounding/stray quotes without invoking a shell."""
    t = tok.strip()
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        t = t[1:-1]
    return t.replace('"', "").replace("'", "")

def _run(project_dir: str, cmd_tokens: List[str]) -> int:
    # Resolve uv (honor UV_EXEC if set)
    uv_exec_name = os.environ.get("UV_EXEC", "uv")
    uv_path = _which(uv_exec_name) or _which("uv") or _which("uvx")
    if not uv_path:
        log.error("uv executable not found on PATH (tried UV_EXEC, then 'uv', then 'uvx').")
        return 4

    # Final argv: keep tokens AS-IS (no injected '--', no reordering)
    argv = [uv_path, "run"] + cmd_tokens if os.path.basename(uv_path) != "uvx" else [uv_path] + cmd_tokens

    os.chdir(project_dir)
    log.info("Changed working directory to: %s", project_dir)
    log.info("Running: %s", " ".join(argv))

    try:
        return subprocess.run(argv, check=False).returncode
    except KeyboardInterrupt:
        log.warning("Interrupted by user")
        return 130
    except Exception as e:
        log.exception("Failed to run: %s", e)
        return 5

def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) < 2:
        print("Usage (recommended):")
        print("  python -m uv_run_module PROJECT_DIR [::] CMD [ARGS ...]")
        print("Examples:")
        print("  python -m uv_run_module /app :: flask run --host=0.0.0.0 --port=80")
        print("  python -m uv_run_module /app :: streamlit run main.py --server.port=8892")
        print("\nBackward-compat (discouraged):")
        print("  python -m uv_run_module PORT PROJECT_DIR [::] CMD [ARGS ...]   (PORT is ignored)")
        return 2

    # New mode: first arg is a directory → PROJECT_DIR first
    first = os.path.abspath(os.path.expanduser(argv[0]))
    if os.path.isdir(first):
        project_dir = first
        rest = [_clean_token(t) for t in argv[1:] if t not in DELIMS]
        if not rest:
            log.error("No command provided after PROJECT_DIR.")
            return 2
        return _run(project_dir, rest)

    # Legacy mode: PORT PROJECT_DIR ... (PORT is ignored)
    if len(argv) >= 3 and _is_int(argv[0]):
        second = os.path.abspath(os.path.expanduser(argv[1]))
        if os.path.isdir(second):
            log.info("Legacy call detected (PORT PROJECT_DIR ...). PORT will be ignored.")
            project_dir = second
            rest = [_clean_token(t) for t in argv[2:] if t not in DELIMS]
            if not rest:
                log.error("No command provided after PROJECT_DIR.")
                return 2
            return _run(project_dir, rest)

    log.error("Could not determine invocation style. Expected PROJECT_DIR first, or legacy PORT PROJECT_DIR.")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())