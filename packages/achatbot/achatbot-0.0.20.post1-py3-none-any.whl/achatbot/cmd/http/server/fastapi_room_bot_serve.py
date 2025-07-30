import asyncio
import logging
import os
import argparse
from contextlib import asynccontextmanager
import traceback
from typing import Dict, List
import json
from asyncio import TimeoutError


from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocketDisconnect
from dotenv import load_dotenv
from fastapi.websockets import WebSocketState

from achatbot.common.utils.helper import ThreadSafeDict
from achatbot.cmd.bots.bridge.base import AISmallWebRTCFastapiWebsocketBot
from achatbot.cmd.bots.base import AIBot
from achatbot.cmd.bots.bot_loader import BotLoader
from achatbot.common.types import CONFIG_DIR
from achatbot.common.const import *
from achatbot.common.logger import Logger
from achatbot.cmd.http.server.fastapi_daily_bot_serve import ngrok_proxy
from achatbot.services.webrtc_peer_connection import SmallWebRTCConnection, IceServer


load_dotenv(override=True)
Logger.init(os.getenv("LOG_LEVEL", "info").upper(), is_file=False, is_console=True)

run_bot: AIBot = None
config = None


# https://fastapi.tiangolo.com/advanced/events/#lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    global run_bot, ws_map, pcs_map, pending_candidates
    try:
        # load model before running
        config_file = config.f if config else os.getenv("CONFIG_FILE")
        run_bot = await BotLoader.load_bot(config_file, bot_type="room_bot")
        run_bot.load()
    except Exception as e:
        print(e)
        traceback.print_exc()

    print(f"load bot {run_bot} success")

    yield  # Run app

    # app life end to clear resources


app = FastAPI(lifespan=lifespan)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制为特定域名
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头部
)


"""
python -m src.cmd.http.server.fastapi_room_bot_serve -f config/bots/dummy_bot.json
"""

if __name__ == "__main__":
    import uvicorn

    default_host = os.getenv("HOST", "0.0.0.0")
    default_port = int(os.getenv("FAST_API_PORT", "4321"))

    parser = argparse.ArgumentParser(description="Fastapi http Room Bot Runner")
    parser.add_argument("--host", type=str, default=default_host, help="Host address")
    parser.add_argument("--port", type=int, default=default_port, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Reload code on change")
    parser.add_argument("--ngrok", action="store_true", help="use ngrok proxy")
    parser.add_argument(
        "-f",
        type=str,
        default=os.path.join(CONFIG_DIR, "bots/dummy_bot.json"),
        help="Bot configuration json file",
    )

    config = parser.parse_args()

    if config.ngrok:
        ngrok_proxy(config.port)

    # Note: not event loop to new on    # api docs: http://0.0.0.0:4321/docs
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        reload=config.reload,
    )
