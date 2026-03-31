from platform import python_version
from threading import RLock
from time import gmtime, strftime
from time import time as t

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pyrogram.types import BotCommand

from Powers import (
    API_HASH, API_ID, BOT_TOKEN, LOG_DATETIME, LOGFILE, LOGGER,
    MESSAGE_DUMP, NO_LOAD, UPTIME, WORKERS, load_cmds,
    scheduler
)
from Powers.plugins import all_plugins
from Powers.plugins.scheduled_jobs import *
from Powers.supports import *
from Powers.vars import Config

INITIAL_LOCK = RLock()

# ===== MongoDB optional setup =====
try:
    from Powers.database import MongoDB
    mongo = MongoDB()
    LOGGER.info("MongoDB initialized successfully")
except Exception:
    mongo = None
    LOGGER.warning("MongoDB disabled, running in memory-only mode")

class Gojo(Client):
    """Pyrogram Bot Client for Gojo_Satoru"""

    def __init__(self):
        super().__init__(
            "Gojo_Satoru",
            bot_token=BOT_TOKEN,
            plugins=dict(root="Powers.plugins", exclude=NO_LOAD),
            api_id=API_ID,
            api_hash=API_HASH,
            workers=WORKERS,
        )

    async def start(self, use_qr=False, except_ids=[]):
        """Start the bot safely."""
        await super().start(use_qr=use_qr, except_ids=except_ids)

        # Set basic commands
        await self.set_bot_commands([
            BotCommand("start", "Check if bot is alive"),
            BotCommand("help", "Get help menu"),
            BotCommand("donate", "Buy me a coffee"),
            BotCommand("bug", "Report bugs")
        ])

        # Get bot info
        meh = await self.get_me()
        Config.BOT_ID = meh.id
        Config.BOT_NAME = meh.first_name
        Config.BOT_USERNAME = meh.username

        # Safe MESSAGE_DUMP start message
        startmsg = None
        if MESSAGE_DUMP:
            try:
                startmsg = await self.send_message(MESSAGE_DUMP, "<i>Starting Bot...</i>")
            except Exception as e:
                LOGGER.warning(f"Failed to send start message: {e}")

        LOGGER.info(f"Pyrogram v{__version__} (Layer {layer}) started on @{meh.username}")
        LOGGER.info(f"Python Version: {python_version()}")

        # Load plugins & commands
        cmd_list = await load_cmds(await all_plugins())
        await load_support_users()
        await cache_support()
        LOGGER.info(f"Dev Users: {SUPPORT_USERS.get('Dev', [])}")
        LOGGER.info(f"Sudo Users: {SUPPORT_USERS.get('Sudo', [])}")
        LOGGER.info(f"Whitelist Users: {SUPPORT_USERS.get('White', [])}")
        LOGGER.info(f"Plugins Loaded: {cmd_list}")

        # Safe scheduler setup (Mongo-dependent jobs skipped if no Mongo)
        if mongo:
            try:
                scheduler.add_job(send_wishish, 'cron', [self], hour=0, minute=0, second=0)
                scheduler.start()
            except Exception as e:
                LOGGER.warning(f"Scheduler skipped due to error: {e}")

        # Update start message with plugin info
        if startmsg:
            try:
                await startmsg.edit_text(
                    f"<b>@{meh.username} started on Pyrogram v{__version__} (Layer {layer})</b>\n"
                    f"<b>Python:</b> <u>{python_version()}</u>\n"
                    f"<b>Loaded Plugins:</b>\n<i>{cmd_list}</i>"
                )
            except Exception:
                pass

        LOGGER.info("Bot started successfully!")

    async def stop(self):
        """Stop bot safely and send logs."""
        runtime = strftime("%Hh %Mm %Ss", gmtime(t() - UPTIME))
        LOGGER.info("Uploading logs before stopping...")

        # Stop scheduler safely
        try:
            scheduler.remove_all_jobs()
        except Exception:
            pass

        # Safe MESSAGE_DUMP or fallback to OWNER_ID
        target = MESSAGE_DUMP or getattr(Config, "OWNER_ID", None)
        if target:
            try:
                await self.send_document(
                    target,
                    document=LOGFILE,
                    caption=f"Bot Stopped!\nUptime: {runtime}\n<code>{LOG_DATETIME}</code>"
                )
            except Exception as e:
                LOGGER.warning(f"Failed to send stop logs: {e}")

        await super().stop()

        # Close Mongo if available
        if mongo:
            try:
                mongo.close()
            except Exception:
                pass

        LOGGER.info(f"Bot stopped successfully. Runtime: {runtime}")
