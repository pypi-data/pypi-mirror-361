from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName, InputUser
from pyrogram.raw.functions.users import GetUsers
from urllib.parse import unquote
from .classes.Exceptions import authDataError
import os

#################################
#     Authentication module     #
#################################

async def update_auth(api_id: int|str = "", api_hash: str = "", session_string: str = "", session_path: str = "", session_name: str = "account") -> str:
    """
    Updates Telegram authData for Portals API using Pyrogram.

    Args:
        api_id (int|str)
        api_hash (str)
        session_string (str) - if you already have a session string, you can pass it here (without passing api_id and api_hash).
        session_path (str, optional) - path where the session file will be saved. Default is current working directory.
        session_name (str, optional) - name of the session file (without extension). Default is "account".

    Returns:
        str: new authData
    """
    if not session_path:
        session_path = os.getcwd()
    if api_id and api_hash and not session_string:
        async with Client(f"{session_name}", api_id=api_id, api_hash=api_hash, workdir=session_path) as client:
            peer = await client.resolve_peer("portals")
            user_full = await client.invoke(GetUsers(id=[peer]))
            bot_raw = user_full[0]
            bot = InputUser(user_id=bot_raw.id, access_hash=bot_raw.access_hash)
            bot_app = InputBotAppShortName(bot_id=bot, short_name="market")
            web_view = await client.invoke(
                RequestAppWebView(
                    peer=peer,
                    app=bot_app,
                    platform="desktop",
                )
            )
            initData = unquote(web_view.url.split('tgWebAppData=', 1)[1].split('&tgWebAppVersion', 1)[0])
            return f"tma {initData}"
    elif session_string:
        async with Client(f"{session_name}", session_string=session_string, workdir=session_path) as client:
            peer = await client.resolve_peer("portals")
            user_full = await client.invoke(GetUsers(id=[peer]))
            bot_raw = user_full[0]
            bot = InputUser(user_id=bot_raw.id, access_hash=bot_raw.access_hash)
            bot_app = InputBotAppShortName(bot_id=bot, short_name="market")
            web_view = await client.invoke(
                RequestAppWebView(
                    peer=peer,
                    app=bot_app,
                    platform="desktop",
                )
            )
            initData = unquote(web_view.url.split('tgWebAppData=', 1)[1].split('&tgWebAppVersion', 1)[0])
            return f"tma {initData}"
    else:
        raise authDataError("aportalsmp: update_auth(): You must provide either api_id and api_hash or a session_string.")