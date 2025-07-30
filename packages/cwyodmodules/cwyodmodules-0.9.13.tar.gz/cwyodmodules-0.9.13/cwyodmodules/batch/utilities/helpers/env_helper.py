import json
import threading                        
# from dotenv import load_dotenv

from ..helpers.config.conversation_flow import ConversationFlow

from mgmt_config import logger, identity, configuration_manager

KEYVAULT_TTL = 3600 # 1 hour

class EnvHelper:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                instance = super(EnvHelper, cls).__new__(cls)
                instance.__load_config()
                cls._instance = instance
            return cls._instance
        
    @logger.trace_function(log_execution=True, log_args=False, log_result=False)
    def __load_config(self, **kwargs) -> None:
        logger.info("Initializing EnvHelper!")
        
        self.AZURE_CLIENT_ID = configuration_manager.get_config(key="AZURE_CLIENT_ID", default="Not set")
        # Wrapper for Azure Key Vault
        configuration_manager.set_config(key="APPLICATIONINSIGHTS_ENABLED", value="true")

        self.LOGLEVEL = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name="logging-level", ttl=KEYVAULT_TTL)
        self.LOG_EXECUTION = self.get_env_var_bool(
                "LOG_EXECUTION", "True"
            )
        self.LOG_ARGS = self.get_env_var_bool(
                "LOG_ARGS", "True"
            )
        self.LOG_RESULT = self.get_env_var_bool(
                "LOG_RESULT", "True"
            )

        # Azure
        self.AZURE_SUBSCRIPTION_ID = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name="subscription-id", ttl=KEYVAULT_TTL)
        self.AZURE_RESOURCE_GROUP = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name="resource-group-name", ttl=KEYVAULT_TTL)
        self.AZURE_HEAD_RESOURCE_GROUP = configuration_manager.get_keyvault_secret(keyvault_name="head", secret_name="resource-group-name", ttl=KEYVAULT_TTL)
        self.AZURE_RESOURCE_ENVIRONMENT = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name="resource-group-environment", ttl=KEYVAULT_TTL)
        self.AZURE_RESOURCE_PRIVATE = (
            configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name="run-private-endpoint", ttl=KEYVAULT_TTL).lower() == "true"
        )
        self.PROJECT_CODE = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name="project-code", ttl=KEYVAULT_TTL)
        self.APP_NAME = configuration_manager.get_config(key="REFLECTION_NAME", default="Default")
        self.POSTGRESQL_NAME = (
            f"psql-main-{self.PROJECT_CODE}-{self.AZURE_RESOURCE_ENVIRONMENT}"
        )
        self.AZURE_AUTH_TYPE = "rbac"
        access_information = identity.get_token_provider(scopes="https://cognitiveservices.azure.com/.default")
        self.AZURE_TOKEN_PROVIDER = access_information
        self.AZURE_BLOB_ACCOUNT_NAME = (
            f"stqueue{self.PROJECT_CODE}{self.AZURE_RESOURCE_ENVIRONMENT}"
        )
        self.AZURE_STORAGE_ACCOUNT_ENDPOINT = (
            f"https://{self.AZURE_BLOB_ACCOUNT_NAME}.blob.core.windows.net/"
        )

        self.AZURE_FUNCTION_APP_ENDPOINT = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name=f"func-backend-{self.PROJECT_CODE}-{self.AZURE_RESOURCE_ENVIRONMENT}-endpoint", ttl=KEYVAULT_TTL
        )
        self.AZURE_BLOB_CONTAINER_NAME = "documents"
        self.DOCUMENT_PROCESSING_QUEUE_NAME = "doc-processing"

        # PostgreSQL configuration - Direct setup without database type switching
        self.AZURE_POSTGRES_SEARCH_TOP_K = 5
        
        # Load PostgreSQL connection details
        azure_postgresql_info = self.get_info_from_env("AZURE_POSTGRESQL_INFO", "")
        if azure_postgresql_info:
            self.POSTGRESQL_USER = azure_postgresql_info.get("user", "")
            self.POSTGRESQL_DATABASE = azure_postgresql_info.get("dbname", "")
            self.POSTGRESQL_HOST = azure_postgresql_info.get("host", "")
        else:
            self.POSTGRESQL_USER = "cwyod_project_uai"
            self.POSTGRESQL_DATABASE = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name=f"{self.POSTGRESQL_NAME}-default-database-name", ttl=KEYVAULT_TTL)
            self.POSTGRESQL_HOST = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name=f"{self.POSTGRESQL_NAME}-server-name", ttl=KEYVAULT_TTL)
        
        # PostgreSQL feature configuration
        self.AZURE_SEARCH_USE_INTEGRATED_VECTORIZATION = False
        self.USE_ADVANCED_IMAGE_PROCESSING = False
        self.CONVERSATION_FLOW = ConversationFlow.CUSTOM.value
        self.ORCHESTRATION_STRATEGY = "semantic_kernel"

        # Azure OpenAI
        self.AZURE_OPENAI_MODEL = "gpt-4o-default"
        self.AZURE_OPENAI_MODEL_NAME = self.AZURE_OPENAI_MODEL
        self.AZURE_OPENAI_VISION_MODEL = "gpt-4"
        self.AZURE_OPENAI_TEMPERATURE = "0"
        self.AZURE_OPENAI_TOP_P = "1.0"
        self.AZURE_OPENAI_MAX_TOKENS = "1500"
        self.AZURE_OPENAI_STOP_SEQUENCE = ""
        self.AZURE_OPENAI_SYSTEM_MESSAGE = (
            "You are an AI assistant that helps people find information."
        )
        self.AZURE_OPENAI_API_VERSION = "2024-02-01"
        self.AZURE_OPENAI_STREAM = "true"
        self.AZURE_OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"

        self.SHOULD_STREAM = (
            True if self.AZURE_OPENAI_STREAM.lower() == "true" else False
        )

        # self.AZURE_COMPUTER_VISION_NAME = head_keyvault.get_secret(
        #     "cognitive-kind-ComputerVision"
        # )
        self.AZURE_COMPUTER_VISION_NAME = ""
        # self.AZURE_COMPUTER_VISION_ENDPOINT = head_keyvault.get_secret(
        #     f"{self.AZURE_COMPUTER_VISION_NAME}-endpoint"
        # )
        self.AZURE_COMPUTER_VISION_ENDPOINT = ""
        self.ADVANCED_IMAGE_PROCESSING_MAX_IMAGES = 1
        self.AZURE_COMPUTER_VISION_TIMEOUT = 30
        self.AZURE_COMPUTER_VISION_VECTORIZE_IMAGE_API_VERSION = "2024-02-01"
        self.AZURE_COMPUTER_VISION_VECTORIZE_IMAGE_MODEL_VERSION = "2023-04-15"

        # Initialize Azure keys based on authentication type and environment settings.
        # When AZURE_AUTH_TYPE is "rbac", azure keys are None or an empty string.
        if self.AZURE_AUTH_TYPE == "rbac":
            self.AZURE_SEARCH_KEY = None
            self.AZURE_OPENAI_API_KEY = ""
            self.AZURE_COMPUTER_VISION_KEY = None
        else:
            self.AZURE_SEARCH_KEY = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name="AZURE_SEARCH_KEY", ttl=KEYVAULT_TTL)
            self.AZURE_OPENAI_API_KEY = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name="AZURE_OPENAI_API_KEY", ttl=KEYVAULT_TTL)
            self.AZURE_COMPUTER_VISION_KEY = configuration_manager.get_keyvault_secret(keyvault_name="main", secret_name="AZURE_COMPUTER_VISION_KEY", ttl=KEYVAULT_TTL)

        # Set env for Azure OpenAI
        self.AZURE_AI_SERVICES_NAME = configuration_manager.get_keyvault_secret(keyvault_name="head", secret_name="cognitive-kind-AIServices", ttl=KEYVAULT_TTL)
        self.AZURE_OPENAI_ENDPOINT = (
            f"https://{self.AZURE_AI_SERVICES_NAME}.openai.azure.com/"
        )

        # Set env for OpenAI SDK
        self.OPENAI_API_TYPE = "azure" if self.AZURE_AUTH_TYPE == "keys" else "azure_ad"
        self.OPENAI_API_KEY = self.AZURE_OPENAI_API_KEY
        self.OPENAI_API_VERSION = self.AZURE_OPENAI_API_VERSION
        configuration_manager.set_config(key="OPENAI_API_TYPE", value=self.OPENAI_API_TYPE, env=True)
        configuration_manager.set_config(key="OPENAI_API_KEY", value=self.OPENAI_API_KEY, env=True)
        configuration_manager.set_config(key="OPENAI_API_VERSION", value=self.OPENAI_API_VERSION, env=True)
        # Azure Functions - Batch processing
        self.BACKEND_URL = self.AZURE_FUNCTION_APP_ENDPOINT
        self.FUNCTION_KEY = None

        # Azure Form Recognizer

        self.AZURE_FORM_RECOGNIZER_NAME = configuration_manager.get_keyvault_secret(keyvault_name="head", secret_name="cognitive-kind-FormRecognizer", ttl=KEYVAULT_TTL)
        self.AZURE_FORM_RECOGNIZER_ENDPOINT = configuration_manager.get_keyvault_secret(keyvault_name="head", secret_name=f"{self.AZURE_FORM_RECOGNIZER_NAME}-endpoint", ttl=KEYVAULT_TTL)

        # Azure App Insights
        # APPLICATIONINSIGHTS_ENABLED will be True when the application runs in App Service
        self.APPLICATIONINSIGHTS_ENABLED = "True"

        # Azure AI Content Safety
        self.AZURE_CONTENT_SAFETY_NAME = configuration_manager.get_keyvault_secret(keyvault_name="head", secret_name="cognitive-kind-ContentSafety", ttl=KEYVAULT_TTL)
        self.AZURE_CONTENT_SAFETY_ENDPOINT = configuration_manager.get_keyvault_secret(keyvault_name="head", secret_name=f"{self.AZURE_CONTENT_SAFETY_NAME}-endpoint", ttl=KEYVAULT_TTL)

        # Speech Service
        self.AZURE_SPEECH_SERVICE_NAME = configuration_manager.get_keyvault_secret(keyvault_name="head", secret_name="cognitive-kind-SpeechServices", ttl=KEYVAULT_TTL)
        self.AZURE_SPEECH_ENDPOINT = configuration_manager.get_keyvault_secret(keyvault_name="head", secret_name=f"{self.AZURE_SPEECH_SERVICE_NAME}-endpoint", ttl=KEYVAULT_TTL)

        self.AZURE_SPEECH_SERVICE_REGION = "westeurope"
        self.AZURE_SPEECH_RECOGNIZER_LANGUAGES = self.get_env_var_array(
            "AZURE_SPEECH_RECOGNIZER_LANGUAGES", "en-US"
        )
        self.AZURE_MAIN_CHAT_LANGUAGE = "en-US"
    
        self.AZURE_SPEECH_REGION_ENDPOINT = (
            f"https://{self.AZURE_SPEECH_SERVICE_REGION}.api.cognitive.microsoft.com/"
        )
        self.AZURE_SPEECH_KEY = configuration_manager.get_keyvault_secret(keyvault_name="head", secret_name=f"{self.AZURE_SPEECH_SERVICE_NAME}-key", ttl=KEYVAULT_TTL) # changed from None to allow private endpoint communication

        self.LOAD_CONFIG_FROM_BLOB_STORAGE = self.get_env_var_bool(
            "LOAD_CONFIG_FROM_BLOB_STORAGE"
        )
        # Azure Search
        self.AZURE_SEARCH_SERVICE = configuration_manager.get_config(key="AZURE_SEARCH_SERVICE", default="")
        self.AZURE_SEARCH_INDEX = configuration_manager.get_config(key="AZURE_SEARCH_INDEX", default="")
        self.AZURE_SEARCH_USE_SEMANTIC_SEARCH = "True"
        self.AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG = configuration_manager.get_config(key="AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG", default="default")
        self.AZURE_SEARCH_INDEX_IS_PRECHUNKED = configuration_manager.get_config(key="AZURE_SEARCH_INDEX_IS_PRECHUNKED", default="")
        self.AZURE_SEARCH_FILTER = configuration_manager.get_config(key="AZURE_SEARCH_FILTER", default="")
        self.AZURE_SEARCH_TOP_K = self.get_env_var_int("AZURE_SEARCH_TOP_K", 5)
        self.AZURE_SEARCH_ENABLE_IN_DOMAIN = (
            configuration_manager.get_config(key="AZURE_SEARCH_ENABLE_IN_DOMAIN", default="true").lower() == "true"
        )
        self.AZURE_SEARCH_FIELDS_ID = configuration_manager.get_config(key="AZURE_SEARCH_FIELDS_ID", default="id")
        self.AZURE_SEARCH_CONTENT_COLUMN = configuration_manager.get_config(key="AZURE_SEARCH_CONTENT_COLUMN", default="content")
        self.AZURE_SEARCH_CONTENT_VECTOR_COLUMN = configuration_manager.get_config(key="AZURE_SEARCH_CONTENT_VECTOR_COLUMN", default="content_vector")
        self.AZURE_SEARCH_DIMENSIONS = configuration_manager.get_config(key="AZURE_SEARCH_DIMENSIONS", default="1536")
        self.AZURE_SEARCH_FILENAME_COLUMN = configuration_manager.get_config(key="AZURE_SEARCH_FILENAME_COLUMN", default="filepath")
        self.AZURE_SEARCH_TITLE_COLUMN = configuration_manager.get_config(key="AZURE_SEARCH_TITLE_COLUMN", default="title")
        self.AZURE_SEARCH_URL_COLUMN = configuration_manager.get_config(key="AZURE_SEARCH_URL_COLUMN", default="url")
        self.AZURE_SEARCH_FIELDS_TAG = configuration_manager.get_config(key="AZURE_SEARCH_FIELDS_TAG", default="tag")
        self.AZURE_SEARCH_FIELDS_METADATA = configuration_manager.get_config(key="AZURE_SEARCH_FIELDS_METADATA", default="metadata")
        self.AZURE_SEARCH_SOURCE_COLUMN = configuration_manager.get_config(key="AZURE_SEARCH_SOURCE_COLUMN", default="source")
        self.AZURE_SEARCH_CHUNK_COLUMN = configuration_manager.get_config(key="AZURE_SEARCH_CHUNK_COLUMN", default="chunk")
        self.AZURE_SEARCH_OFFSET_COLUMN = configuration_manager.get_config(key="AZURE_SEARCH_OFFSET_COLUMN", default="offset")
        self.AZURE_SEARCH_CONVERSATIONS_LOG_INDEX = configuration_manager.get_config(key="AZURE_SEARCH_CONVERSATIONS_LOG_INDEX", default="conversations")
        self.AZURE_SEARCH_DOC_UPLOAD_BATCH_SIZE = configuration_manager.get_config(key="AZURE_SEARCH_DOC_UPLOAD_BATCH_SIZE", default=100)
        # Integrated Vectorization


        self.AZURE_ML_WORKSPACE_NAME = ""

        self.PROMPT_FLOW_ENDPOINT_NAME = ""

        self.PROMPT_FLOW_DEPLOYMENT_NAME = ""

        self.OPEN_AI_FUNCTIONS_SYSTEM_PROMPT = ""
        self.SEMENTIC_KERNEL_SYSTEM_PROMPT = ""

        logger.info("Initializing EnvHelper completed")

    def is_chat_model(self):
        if "gpt-4" in self.AZURE_OPENAI_MODEL_NAME.lower():
            return True
        return False

    def get_env_var_bool(self, var_name: str, default: str = "True") -> bool:
        return configuration_manager.get_config(key=var_name, default=default).lower() == "true"

    def get_env_var_array(self, var_name: str, default: str = ""):
        return configuration_manager.get_config(key=var_name, default=default).split(",")

    def get_env_var_int(self, var_name: str, default: int):
        try:
            return int(configuration_manager.get_config(key=var_name, default=default))
        except (ValueError, TypeError):
            return default

    def get_env_var_float(self, var_name: str, default: float):
        try:
            return float(configuration_manager.get_config(key=var_name, default=default))
        except (ValueError, TypeError):
            return default

    def is_auth_type_keys(self):
        return self.AZURE_AUTH_TYPE == "keys"

    def get_info_from_env(self, env_var: str, default_info: str) -> dict:
        # Fetch and parse model info from the environment variable.
        info_str = configuration_manager.get_config(key=env_var, default=default_info)
        # Handle escaped characters in the JSON string by wrapping it in double quotes for parsing.
        if "\\" in info_str:
            info_str = json.loads(f'"{info_str}"')
        try:
            return {} if not info_str else json.loads(info_str)
        except (json.JSONDecodeError, ValueError, TypeError):
            try:
                return json.loads(default_info) if default_info else {}
            except (json.JSONDecodeError, ValueError, TypeError):
                return {}

    @staticmethod
    def check_env():
        for attr, value in EnvHelper().__dict__.items():
            if value == "" or value is None:
                logger.warning(f"{attr} is not set in the environment variables.")

    @classmethod
    def clear_instance(cls):
        if cls._instance is not None:
            cls._instance = None
