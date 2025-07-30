from ..helpers.azure_search_helper import AzureSearchHelper
from datetime import datetime
import json

class ConversationLogger:
    """
    A logger class for logging user and assistant messages in a conversation.

    This class uses AzureSearchHelper to log messages with metadata such as
    conversation ID, message type, and timestamps.
    """

    def __init__(self):
        """
        Initializes the ConversationLogger instance.

        Sets up the logger using AzureSearchHelper.
        """
        self.logger = AzureSearchHelper().get_conversation_logger()

    def log(self, data: dict):
        """
        Logs a dictionary of data to the search index.

        Args:
            data (dict): A dictionary of data to be logged.
        """
        data["created_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.logger.upload_documents(documents=[data])