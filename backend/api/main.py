import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from config import Config
from db import seed_database, set_main_loop
from graph import create_workflow
from logger import log
from vectorstore import seed_vectors

from .routes import api_router

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Initializing system...")
    # Register the main event loop so worker threads can schedule DB coroutines on it.
    set_main_loop(asyncio.get_running_loop())

    # ── Database ──────────────────────────────────────────────────────────────
    try:
        await seed_database()
    except Exception as exc:
        log.critical(
            f"[STARTUP FAILED] Database connection error: {exc}\n"
            f"  → Ensure PostgreSQL is running and DATABASE_URL is correct."
        )
        sys.exit(1)

    # ── Vector store ──────────────────────────────────────────────────────────
    try:
        seed_vectors()
    except ConnectionError as exc:
        log.critical(
            f"[STARTUP FAILED] Vector store connection error: {exc}\n"
            f"  → Start Qdrant with:  docker compose up qdrant"
        )
        sys.exit(1)
    except Exception as exc:
        log.critical(
            f"[STARTUP FAILED] Vector store initialization error: {exc}\n"
            f"  → Check Qdrant configuration in config.py."
        )
        sys.exit(1)

    # ── Workflow / checkpointer ───────────────────────────────────────────────
    connection_kwargs = {"autocommit": True, "prepare_threshold": 0}
    try:
        async with AsyncConnectionPool(
            conninfo=Config.DATABASE_URL,
            max_size=10,
            kwargs=connection_kwargs,
            open=False,
        ) as pool:
            await pool.open()
            checkpointer = AsyncPostgresSaver(pool)
            await checkpointer.setup()
            app.state.workflow = create_workflow(checkpointer)
            log.info("System initialized successfully")
            yield
    except Exception as exc:
        log.critical(
            f"[STARTUP FAILED] Workflow initialization error: {exc}\n"
            f"  → Check PostgreSQL connectivity and credentials."
        )
        sys.exit(1)


app = FastAPI(title="Ecom API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# Serve the built React app in production.
if FRONTEND_DIST.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="assets",
    )

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # API routes are handled above; everything else returns index.html
        # so client-side routing works.
        index = FRONTEND_DIST / "index.html"
        return FileResponse(index)
