import requests
import logging
from .base import WhatsAppProvider
from typing import Union, Tuple, Dict, Any

logger = logging.getLogger("Novomind.Notifications.Whatsapp")

class NovomindWhatsAppNotifications(WhatsAppProvider):
    def __init__(self, endpoint: str, config: Union[str, dict]):
        super().__init__(endpoint, config)
        self.token = self.config.get("token")
        self.client_id = self.config.get("CLIENT_ID")
        self.account_id = self.config.get("ACCOUNT_ID")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def send(self, recipient: str, messagePayload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Executes the full send pipeline: create participant, conversation, and send the message.
        Returns (True, success_message) on success, or (False, error_message) on failure.
        """
        logger.info("Initiating WhatsApp send pipeline for recipient: %s", recipient)

        if not recipient:
            error_msg = "Recipient (WhatsApp ID) is required but was not provided."
            logger.error(error_msg)
            return False, error_msg

        try:
            participant_id = self._create_participant(recipient)
            logger.info("Participant created successfully: %s", participant_id)

            conversation_id = self._create_conversation(participant_id)
            logger.info("Conversation created successfully: %s", conversation_id)

            self._send_message(conversation_id, messagePayload)
            logger.info("Message sent successfully for conversation: %s", conversation_id)

            return True, "Message sent successfully"
        except requests.RequestException as e:
            try:
                error_response = e.response.json()
                error_msg = error_response.get("message", str(error_response))
            except Exception:
                error_msg = str(e)
            logger.error("Error during WhatsApp send pipeline: %s", error_msg)
            return False, error_msg

    def _create_participant(self, whatsapp_id: str) -> str:
        url = f"{self.endpoint}clients/{self.client_id}/participants"
        payload = {
            "channel": "whatsapp",
            "whatsapp_id": whatsapp_id
        }
        logger.debug("Creating participant with payload: %s", payload)
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["id"]

    #-----------------------------------------------------------------------------------------
    def _create_conversation(self, participant_id: str) -> str:
        url = f"{self.endpoint}clients/{self.client_id}/conversations"
        payload = {
            "channel": "whatsapp",
            "type": "individual",
            "account_id": self.account_id,
            "participant_id": participant_id
        }
        logger.debug("Creating conversation with payload: %s", payload)
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["id"]
    
    #-----------------------------------------------------------------------------------------
    def _send_message(self, conversation_id: str, payload: dict) -> dict:

        if not isinstance(payload, dict):
            raise TypeError("Invalid payload type, expected a dictionary.")

        url = f"{self.endpoint}clients/{self.client_id}/conversations/{conversation_id}/messages"

        logger.debug("Sending message with payload: %s", payload)
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    # def _send_message(self, conversation_id: str, payload_data: dict) -> dict:
    #     # 🔐 Validate required fields
    #     required_fields = ["template"]
    #     missing = [field for field in required_fields if not payload_data.get(field)]

    #     if len(missing) > 0:
    #         error_msg = f"Missing required template fields: {', '.join(missing)}"
    #         logger.error(error_msg)
    #         raise ValueError(error_msg)

    #     # ✅ Extract values after validation
    #     template_name = payload_data.get("template")
    #     customer_name = payload_data.get("customer_name")
    #     subject = payload_data.get("subject")
    #     date = payload_data.get("date")
    #     time = payload_data.get("time")
    #     language = payload_data.get("language", "en")

    #     url = f"{self.endpoint}clients/{self.client_id}/conversations/{conversation_id}/messages"

    #     payload = {
    #         "passthrough": {
    #             "template": {
    #                 "components": [
    #                     {
    #                         "type": "body",
    #                         "parameters": [
    #                             {"type": "text", "text": customer_name},
    #                             {"type": "text", "text": subject},
    #                             {"type": "text", "text": date},
    #                             {"type": "text", "text": time}
    #                         ]
    #                     },
    #                     {
    #                         "type": "header",
    #                         "parameters": [
    #                             {
    #                                 "type": "image",
    #                                 "image": {
    #                                     "filename": "image",
    #                                     "id": "nQ2XorfSCH08z1xBKKbNveiP"
    #                                 }
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "namespace": self.namespace,
    #                 "name": template_name,
    #                 "language": {
    #                     "code": language,
    #                     "policy": "deterministic"
    #                 }
    #             },
    #             "type": "template"
    #         },
    #         "type": "passthrough"
    #     }

    #     logger.debug("Sending message with payload: %s", payload)
    #     response = requests.post(url, headers=self.headers, json=payload)
    #     response.raise_for_status()
    #     return response.json()