from importlib.metadata import version
from .whatsapp.notifications import WhatsAppNotifications
from .config import AssignmentConfig

__version__ = version("agentix-notifications")

__all__ = ["WhatsAppNotifications", "__version__", "AssignmentConfig"]