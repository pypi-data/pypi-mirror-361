import json
from abc import ABC, abstractmethod
from typing import Union

class WhatsAppProvider(ABC):
    def __init__(self, endpoint: str, config: Union[str, dict]):
        self.endpoint = endpoint
        self.config = self._parse_config(config)

    @staticmethod
    def _parse_config(config: Union[str, dict]) -> dict:
        if isinstance(config, str):
            try:
                return json.loads(config)
            except json.JSONDecodeError as e:
                raise ValueError("Invalid JSON string for provider config.") from e
        elif isinstance(config, dict):
            return config
        else:
            raise TypeError("Config must be a dictionary or a JSON string.")

    @abstractmethod
    def send(self, recipient: str, message: str) -> dict:
        pass