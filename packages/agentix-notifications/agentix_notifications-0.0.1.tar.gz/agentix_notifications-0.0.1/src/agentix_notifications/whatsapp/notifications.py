from .novomind import NovomindWhatsAppNotifications
from typing import Union, Dict, Any, Tuple

class WhatsAppNotifications:
    def __init__(self, provider_name: str = None, config: Union[str, dict] = None):
        """Initialize WhatsAppNotifications with a specific provider and configuration.
        Args:
            provider_name (str): The name of the WhatsApp provider (e.g., "NOVOMIND").
            config (Union[str, dict]): The configuration for the WhatsApp provider.
        Raises:
            ValueError: If the provider name or configuration is not provided, or if the configuration is invalid.
        """
        self._provider = None
        self._provider_name = provider_name

        if not provider_name or not config:
            raise ValueError("Provider name and configuration must be provided.")

        provider = provider_name.strip().upper()
        if provider == "NOVOMIND":
            endpoint = config.get("endpoint", None)
            provider_config = config.get("config", None)
            
            if not endpoint or not provider_config or not isinstance(provider_config, dict):
                raise ValueError("Missing or invalid 'endpoint' or 'config' in WhatsApp configuration.")
            
            self._provider = NovomindWhatsAppNotifications(endpoint, provider_config)
        else:
            raise ValueError(f"Unsupported WhatsApp provider: {provider_name}")

    # ==================================================================================================
    # Send WhatsApp Message
    # ==================================================================================================
    def send(self, recipient: str, message_payload: Dict[str, Any]) -> Tuple[bool, str]:
        """Send a WhatsApp message to the specified recipient.
        Args:
            recipient (str): The phone number of the recipient.
            message_payload (Dict[str, Any]): The payload containing the message details.
        Returns:
            Tuple[bool, str]: A tuple containing a success flag and a message.
        Raises:
            ValueError: If the WhatsApp provider is not configured.
        """
        if not self._provider:
            raise ValueError("WhatsApp provider is not configured.")
        
        return self._provider.send(recipient, message_payload)

    # def NOVOMIND(self, endpoint: str, config: Union[str, dict]):
    #     self._provider = NovomindWhatsAppNotifications(endpoint, config)
    #     return self