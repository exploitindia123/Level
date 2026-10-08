# server.py — Railway entry point
import os, asyncio, threading, json
from pathlib import Path
from aiohttp import web

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

# ---- bot ko background thread mein chala ----
_bot_thread = None

def start_bot():
    import main as bot_main
    try:
        asyncio.run(bot_main.main())
    except Exception as e:
        print(f"[server] bot crashed: {e}", flush=True)

def ensure_bot_running():
    global _bot_thread
    if _bot_thread is None or not _bot_thread.is_alive():
        _bot_thread = threading.Thread(target=start_bot, daemon=True)
        _bot_thread.start()

# ---- dashboard_server ke routes reuse kar ----
# Agar tera dashboard_server.py aiohttp app banata hai, toh
# usse yahan import karke same app pe serve kar.
try:
    from dashboard_server import create_app  # agar tu aisa function banaye
    app = create_app()
except Exception:
    app = web.Application()

async def root(request):
    # index.html serve kar
    html = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
    return web.Response(text=html, content_type="text/html")

if not any(r.resource.canonical == "/" for r in app.router.routes()):
    app.router.add_get("/", root)

async def on_startup(_):
    ensure_bot_running()

app.on_startup.append(on_startup)

if __name__ == "__main__":
    web.run_app(app, host=HOST, port=PORT)
