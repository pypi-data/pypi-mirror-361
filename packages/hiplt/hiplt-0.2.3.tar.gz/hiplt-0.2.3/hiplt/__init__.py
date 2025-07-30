# hiplt/__init__.py

__version__ = "0.2.2"

# Основные модули
from .core import *
from .plugins import *
from .cmd import *
from .net import *
from .config import *
from .system import *
from .bridge import *

# Расширения и утилиты
from .scheduler import Scheduler
from .router import Router
from .acs import AccessControlSystem, AccessDenied
from .locale import LocaleManager
from .utils import now_iso, ensure_dir, setup_logger
from .shell import Shell

# GUI — защищённый импорт (работает только если tkinter доступен)
try:
    from .gui import GUIApp
except ImportError:
    GUIApp = None
    print("⚠️ GUI отключён — tkinter не поддерживается на этой платформе.")

from .telemetry import Telemetry
from .db import Database
from .types import *