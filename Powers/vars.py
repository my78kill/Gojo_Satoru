from os import getcwd, path
from prettyconf import Configuration
from prettyconf.loaders import EnvFile, Environment

env_file = f"{getcwd()}/.env"
config = Configuration(loaders=[Environment(), EnvFile(filename=env_file)])
is_env = path.isfile(env_file)


class Config:
    """Config class for variables."""

    LOGGER = True
    BOT_TOKEN = config("BOT_TOKEN", default=None)
    API_ID = int(config("API_ID", default="123"))
    API_HASH = config("API_HASH", default=None)
    OWNER_ID = int(config("OWNER_ID", default=1344569458))
    MESSAGE_DUMP = int(config("MESSAGE_DUMP", default="0"))
    DEV_USERS = [int(i) for i in config("DEV_USERS", default="").split() if i]
    SUDO_USERS = [int(i) for i in config("SUDO_USERS", default="").split() if i]
    WHITELIST_USERS = [int(i) for i in config("WHITELIST_USERS", default="").split() if i]
    GENIUS_API_TOKEN = config("GENIUS_API", default=None)
    RMBG_API = config("RMBG_API", default=None)
    DB_URI = config("DB_URI", default=None)
    DB_NAME = config("DB_NAME", default="gojo_satarou")
    BDB_URI = config("BDB_URI", default=None)
    NO_LOAD = config("NO_LOAD", default="").split()
    PREFIX_HANDLER = config("PREFIX_HANDLER", default="/").split()
    SUPPORT_GROUP = config("SUPPORT_GROUP", default="gojo_bots_network")
    SUPPORT_CHANNEL = config("SUPPORT_CHANNEL", default="gojo_bots_network")
    WORKERS = int(config("WORKERS", default=16))
    TIME_ZONE = config("TIME_ZONE", default='Asia/Kolkata')
    BOT_USERNAME = ""
    BOT_ID = ""
    BOT_NAME = ""


class Development(Config):
    """Fallback Development class if no .env is found."""
    BOT_TOKEN = "YOUR BOT_TOKEN"
    API_ID = 12345
    API_HASH = "YOUR API HASH"
    OWNER_ID = 1344569458
    MESSAGE_DUMP = 0
    DEV_USERS = []
    SUDO_USERS = []
    WHITELIST_USERS = []
    DB_URI = ""
    DB_NAME = ""
    GENIUS_API_TOKEN = ""
    RMBG_API = ""
    NO_LOAD = []
    PREFIX_HANDLER = ["!", "/", "$"]
    SUPPORT_GROUP = "SUPPORT_GROUP"
    SUPPORT_CHANNEL = "SUPPORT_CHANNEL"
    VERSION = "0.0"
    TIME_ZONE = 'Asia/Kolkata'
    WORKERS = 8
