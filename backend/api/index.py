import os
import sys

# Ensure Python can import from both `backend/` and repository root
_current_dir = os.path.dirname(__file__)
_project_root = os.path.abspath(os.path.join(_current_dir, ".."))
_repo_root = os.path.abspath(os.path.join(_project_root, ".."))
for _p in (_project_root, _repo_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from app.main import app
except Exception as e:
    try:
        from backend.app.main import app  # type: ignore
    except Exception as inner:
        import traceback
        print("[Vercel] Failed to import FastAPI app:", e, file=sys.stderr)
        traceback.print_exc()
        # Provide a minimal ASGI app fallback to avoid cold-start crashes on serverless
        try:
            from fastapi import FastAPI

            _fallback = FastAPI()

            @_fallback.get("/health")
            def _health():
                # Expose degraded state so the deployment stays alive and returns a helpful message
                return {"status": "degraded", "error": str(e)}

            app = _fallback
        except Exception:
            # If even the fallback cannot be created, re-raise the original import error
            raise

# Vercel’s Python serverless runtime auto-detects `app` as ASGI application.