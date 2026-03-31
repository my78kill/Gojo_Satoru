import shutil
from datetime import datetime
from importlib import import_module as imp_mod
from logging import (INFO, WARNING, FileHandler, StreamHandler, basicConfig, getLogger)
from os import environ, listdir, mkdir, path
from platform import python_version
from sys import exit as sysexit, stdout, version_info
from time import time
from traceback import format_exc

# Optional imports
try:
    import pyrogram
except ImportError:
    print("Pyrogram not installed! Install with `pip install pyrogram tgcrypto`")
    sysexit(1)

try:
    import lyricsgenius
    LYRICSGENIUS_INSTALLED = True
except ImportError:
    LYRICSGENIUS_INSTALLED = False

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Logging setup
LOG_DATETIME = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
LOGDIR = "./logs"
if path.isdir(LOGDIR):
    shutil.rmtree(LOGDIR)
mkdir(LOGDIR)
LOGFILE = f"{LOGDIR}/log_{LOG_DATETIME}.txt"

file_handler = FileHandler(filename=LOGFILE)
stdout_handler = StreamHandler(stdout)

basicConfig(
    format="%(asctime)s - [Gojo_Satoru] - %(levelname)s - %(message)s",
    level=INFO,
    handlers=[file_handler, stdout_handler],
)

getLogger("pyrogram").setLevel(WARNING)
LOGGER = getLogger(__name__)

# Python version check
if version_info[0] < 3 or version_info[1] < 7:
    LOGGER.error("Python >= 3.7 required. Quitting...")
    sysexit(1)

# Config import
try:
    from Powers.vars import is_env
    if is_env or environ.get("ENV"):
        from Powers.vars import Config
    else:
        from Powers.vars import Development as Config
except Exception as ef:
    LOGGER.error(ef)
    LOGGER.error(format_exc())
    sysexit(1)

# Timezone
TIME_ZONE = pytz.timezone(Config.TIME_ZONE)

# Version safe
try:
    version_files = [i for i in listdir("./Version") if i.startswith("version") and i.endswith("md")]
    VERSION = sorted(version_files)[-1][8:-3] if version_files else "0.0"
except FileNotFoundError:
    VERSION = "0.0"

PYTHON_VERSION = python_version()
PYROGRAM_VERSION = pyrogram.__version__

LOGGER.info("------------------------")
LOGGER.info("|      Gojo_Satoru      |")
LOGGER.info("------------------------")
LOGGER.info(f"Version: {VERSION}")
LOGGER.info(f"Owner: {str(Config.OWNER_ID)}")
LOGGER.info(f"Time zone set to {Config.TIME_ZONE}")
LOGGER.info("Source Code: https://github.com/Gojo-Bots/Gojo_Satoru\n")

# Genius API setup
if LYRICSGENIUS_INSTALLED and Config.GENIUS_API_TOKEN:
    LOGGER.info("Initializing Genius client...")
    genius_lyrics = lyricsgenius.Genius(
        Config.GENIUS_API_TOKEN,
        skip_non_songs=True,
        excluded_terms=["(Remix)", "(Live)"],
        remove_section_headers=True,
    )
    genius_lyrics.verbose = False
    is_genius_lyrics = True
else:
    if not LYRICSGENIUS_INSTALLED:
        LOGGER.warning("lyricsgenius not installed, lyrics plugin disabled")
    is_genius_lyrics = False
    genius_lyrics = None

# RMBG
is_rmbg = bool(Config.RMBG_API)
RMBG = Config.RMBG_API if is_rmbg else None

# Account
BOT_TOKEN = Config.BOT_TOKEN
API_ID = Config.API_ID
API_HASH = Config.API_HASH
OWNER_ID = Config.OWNER_ID
MESSAGE_DUMP = Config.MESSAGE_DUMP or OWNER_ID

# Support Users
SUPPORT_USERS = {
    "Owner": [OWNER_ID],
    "Dev": set(Config.DEV_USERS),
    "Sudo": set(Config.SUDO_USERS),
    "White": set(Config.WHITELIST_USERS),
}

# General Config
SUPPORT_GROUP = Config.SUPPORT_GROUP
SUPPORT_CHANNEL = Config.SUPPORT_CHANNEL

# DB / Plugins
DB_URI = Config.DB_URI
DB_NAME = Config.DB_NAME
BDB_URI = Config.BDB_URI
NO_LOAD = Config.NO_LOAD
WORKERS = Config.WORKERS

# Prefixes
PREFIX_HANDLER = Config.PREFIX_HANDLER

HELP_COMMANDS = {}
UPTIME = time()

# Directories
for d in ["./Youtube/", "./scrapped/"]:
    if path.isdir(d):
        shutil.rmtree(d)
    mkdir(d)

scheduler = AsyncIOScheduler(timezone=TIME_ZONE)


async def load_cmds(all_plugins):
    """Load all plugins safely."""
    for single in all_plugins:
        if single.lower() in [i.lower() for i in Config.NO_LOAD]:
            LOGGER.warning(f"Skipping '{single}' (in NO_LOAD)")
            continue

        mod = imp_mod(f"Powers.plugins.{single}")
        if not hasattr(mod, "__PLUGIN__"):
            continue

        pname = mod.__PLUGIN__.lower()
        pdict = f"plugins.{pname}"
        HELP_COMMANDS[pdict] = {
            "buttons": getattr(mod, "__buttons__", []),
            "disablable": getattr(mod, "_DISABLE_CMDS_", []),
            "alt_cmds": getattr(mod, "__alt_name__", []),
            "help_msg": getattr(mod, "__HELP__", ""),
        }
        HELP_COMMANDS[pdict]["alt_cmds"].append(pname)

    if NO_LOAD:
        LOGGER.warning(f"Not loading Plugins: {NO_LOAD}")
    return ", ".join((i.split(".")[1]).capitalize() for i in HELP_COMMANDS.keys()) + "\n"
