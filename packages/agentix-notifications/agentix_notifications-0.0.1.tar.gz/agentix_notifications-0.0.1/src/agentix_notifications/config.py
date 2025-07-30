import json
import re
import base64
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple

# from .turn_detector_config import TurnDetectorConfig  # adjust the path if needed

logger = logging.getLogger("config")

@dataclass
class AssignmentConfig:
    # handoff_provider: str = "OFF"
    # handoff_provider_config: str = ""
    # handoff_plugin_url: str = ""

    whatsapp_notification_provider: str = "OFF"
    whatsapp_notification_config: dict = field(default_factory=dict)

    # live_assist_agent: str = "OFF"


    @staticmethod
    def from_dict(assignment_dict: Dict[str, Any]) -> "AssignmentConfig":
        try:
            config = AssignmentConfig()
            config_items = assignment_dict.get("configs", [])

            # Build a key-value map from nested structure
            task_config = {}
            for entry in config_items:
                schema = entry.get("agent_config_schema")
                if not schema or not isinstance(schema, dict):
                    continue  # Skip malformed or missing config schema

                key = schema.get("key")
                value = entry.get("value")

                if key and value is not None:
                    task_config[key] = value

            
            # config.handoff_provider, config.handoff_provider_config = AssignmentConfig.parse_provider_model(
            #     task_config.get("HANDOFF", "OFF"), to_lower=False
            # )
            
            # config.handoff_plugin_url = task_config.get("HANDOFF_PLUGIN_URL", "").strip()

            # config.live_assist_agent = task_config.get("HANDOFF_LIVE_ASSIST_AGENT", "OFF").strip()
            
            whatsapp_notification_config_str: str
            config.whatsapp_notification_provider, whatsapp_notification_config_str = AssignmentConfig.parse_provider_model(
                task_config.get("WHATSAPP_NOTIFICATION", "OFF"), to_lower=False
            )
            decoded_json_str = ""
            if whatsapp_notification_config_str:
                try:
                    decoded_json_str = base64.b64decode(
                        whatsapp_notification_config_str.strip()
                    ).decode("utf-8")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to decode WhatsApp config: {e}")

            config.whatsapp_notification_config = AssignmentConfig.load_json_safely(decoded_json_str)

            return config
        
        except Exception as e:
            logger.error(f"❌ Unexpected error while parsing assignment config: {e}")
            raise ValueError("Failed to parse assignment config, using default values.")
    
    @staticmethod
    def safe_float(value, default: float) -> float:
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"⚠️ Invalid float value '{value}', falling back to default: {default}")
            return default
        

    @staticmethod
    def safe_int(value, default: int) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"⚠️ Invalid int value '{value}', falling back to default: {default}")
            return default

    @staticmethod
    def parse_provider_model(raw_value: str, splitter: str = ":", to_lower: bool = True) -> tuple:
        raw_value = re.sub(r'[\r\n]+', '', str(raw_value or ""))
        parts = raw_value.split(splitter, 1)
        if to_lower:
            return (parts[0].lower(), parts[1]) if len(parts) > 1 else (parts[0].lower(), "")
        else:
            return (parts[0], parts[1]) if len(parts) > 1 else (parts[0], "")

    @staticmethod
    def load_json_safely(text: str) -> dict:
        if not isinstance(text, str):
            logger.warning("Expected a string for JSON parsing, got: %s", type(text).__name__)
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON string: %s", str(e))
            return {}
