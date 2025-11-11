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
            from fastapi import FastAPI, Response, HTTPException
            from fastapi.middleware.cors import CORSMiddleware

            _fallback = FastAPI()

            # Match main app CORS settings so preflight succeeds for the frontend
            _fallback.add_middleware(
                CORSMiddleware,
                allow_origins=[
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://10.10.247.154:3000",
                    "https://viswanth207.github.io",
                    "https://meal-planner-ai-upay.vercel.app",
                ],
                allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            @_fallback.get("/health")
            def _health():
                # Expose degraded state so the deployment stays alive and returns a helpful message
                return {"status": "degraded", "error": str(e)}

            @_fallback.get("/favicon.ico")
            def _favicon():
                # Quiet browser's automatic favicon request
                return Response(status_code=204)

            @_fallback.get("/")
            def _root():
                # Simple text response to confirm deployment routing
                return Response(content="hi", media_type="text/plain")

            # Clarify auth endpoints when fallback is serving and support preflight
            @_fallback.get("/auth/signup")
            def _fallback_signup_get():
                raise HTTPException(status_code=405, detail="Method Not Allowed. Use POST.")

            @_fallback.options("/auth/signup")
            def _fallback_signup_options():
                return Response(status_code=204)

            @_fallback.get("/auth/login")
            def _fallback_login_get():
                raise HTTPException(status_code=405, detail="Method Not Allowed. Use POST.")

            @_fallback.options("/auth/login")
            def _fallback_login_options():
                return Response(status_code=204)

            app = _fallback
        except Exception:
            # If even the fallback cannot be created, re-raise the original import error
            raise

# Vercel’s Python serverless runtime auto-detects `app` as ASGI application.