import os
import json
import functools
from string import Template

from ...document_chunking.chunking_strategy import ChunkingStrategy, ChunkingSettings
from ...document_loading import LoadingSettings, LoadingStrategy
from .embedding_config import EmbeddingConfig

from ..env_helper import EnvHelper
from .assistant_strategy import AssistantStrategy
from .conversation_flow import ConversationFlow


CONFIG_CONTAINER_NAME = "config"
CONFIG_FILE_NAME = "active.json"
ADVANCED_IMAGE_PROCESSING_FILE_TYPES = ["jpeg", "jpg", "png", "tiff", "bmp"]

from mgmt_config import logger, storage_account
env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT


class Config:
    def __init__(self, config: dict):
        self.prompts = Prompts(config["prompts"])
        self.messages = Messages(config["messages"])
        self.example = Example(config["example"])
        self.logging = Logging(config["logging"])
        self.document_processors = [
            EmbeddingConfig(
                document_type=c["document_type"],
                chunking=ChunkingSettings(c["chunking"]),
                loading=LoadingSettings(c["loading"]),
                use_advanced_image_processing=c.get(
                    "use_advanced_image_processing", False
                ),
            )
            for c in config["document_processors"]
        ]
        self.env_helper = EnvHelper()
        # Orchestrator is always semantic kernel now
        # No configuration needed as there's only one option
        self.integrated_vectorization_config = (
            IntegratedVectorizationConfig(config["integrated_vectorization_config"])
            if self.env_helper.AZURE_SEARCH_USE_INTEGRATED_VECTORIZATION
            else None
        )
        self.enable_chat_history = config["enable_chat_history"]
        self.conversational_flow = config.get(
            "conversational_flow", self.env_helper.CONVERSATION_FLOW
        )

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def get_available_document_types(self) -> list[str]:
        document_types = {
            "txt",
            "pdf",
            "url",
            "html",
            "htm",
            "md",
            "jpeg",
            "jpg",
            "png",
            "docx",
        }
        if self.env_helper.USE_ADVANCED_IMAGE_PROCESSING:
            document_types.update(ADVANCED_IMAGE_PROCESSING_FILE_TYPES)

        return sorted(document_types)

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def get_advanced_image_processing_image_types(self):
        return ADVANCED_IMAGE_PROCESSING_FILE_TYPES

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def get_available_chunking_strategies(self):
        return [c.value for c in ChunkingStrategy]

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def get_available_loading_strategies(self):
        return [c.value for c in LoadingStrategy]

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def get_available_orchestration_strategies(self):
        return ["semantic_kernel"]  # Only semantic kernel is supported now

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def get_available_ai_assistant_types(self):
        return [c.value for c in AssistantStrategy]

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def get_available_conversational_flows(self):
        return [c.value for c in ConversationFlow]


# TODO: Change to AnsweringChain or something, Prompts is not a good name
class Prompts:
    def __init__(self, prompts: dict):
        self.condense_question_prompt = prompts["condense_question_prompt"]
        self.answering_system_prompt = prompts["answering_system_prompt"]
        self.answering_user_prompt = prompts["answering_user_prompt"]
        self.post_answering_prompt = prompts["post_answering_prompt"]
        self.use_on_your_data_format = prompts["use_on_your_data_format"]
        self.enable_post_answering_prompt = prompts["enable_post_answering_prompt"]
        self.enable_content_safety = prompts["enable_content_safety"]
        self.ai_assistant_type = prompts["ai_assistant_type"]
        self.conversational_flow = prompts["conversational_flow"]


class Example:
    def __init__(self, example: dict):
        self.documents = example["documents"]
        self.user_question = example["user_question"]
        self.answer = example["answer"]


class Messages:
    def __init__(self, messages: dict):
        self.post_answering_filter = messages["post_answering_filter"]


class Logging:
    def __init__(self, logging: dict):
        self.log_user_interactions = (
            str(logging["log_user_interactions"]).lower() == "true"
        )
        self.log_tokens = str(logging["log_tokens"]).lower() == "true"


class IntegratedVectorizationConfig:
    def __init__(self, integrated_vectorization_config: dict):
        self.max_page_length = integrated_vectorization_config["max_page_length"]
        self.page_overlap_length = integrated_vectorization_config[
            "page_overlap_length"
        ]


class ConfigHelper:
    _default_config = None

    @staticmethod
    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def _set_new_config_properties(config: dict, default_config: dict):
        """
        Function used to set newer properties that will not be present in older configs.
        The function mutates the config object.
        """
        if config["prompts"].get("answering_system_prompt") is None:
            config["prompts"]["answering_system_prompt"] = default_config["prompts"][
                "answering_system_prompt"
            ]

        prompt_modified = (
            config["prompts"].get("answering_prompt")
            != default_config["prompts"]["answering_prompt"]
        )

        if config["prompts"].get("answering_user_prompt") is None:
            if prompt_modified:
                config["prompts"]["answering_user_prompt"] = config["prompts"].get(
                    "answering_prompt"
                )
            else:
                config["prompts"]["answering_user_prompt"] = default_config["prompts"][
                    "answering_user_prompt"
                ]

        if config["prompts"].get("use_on_your_data_format") is None:
            config["prompts"]["use_on_your_data_format"] = not prompt_modified

        if config.get("example") is None:
            config["example"] = default_config["example"]

        if config["prompts"].get("ai_assistant_type") is None:
            config["prompts"]["ai_assistant_type"] = default_config["prompts"][
                "ai_assistant_type"
            ]

        if config.get("integrated_vectorization_config") is None:
            config["integrated_vectorization_config"] = default_config[
                "integrated_vectorization_config"
            ]

        if config["prompts"].get("conversational_flow") is None:
            config["prompts"]["conversational_flow"] = default_config["prompts"][
                "conversational_flow"
            ]
        if config.get("enable_chat_history") is None:
            config["enable_chat_history"] = default_config["enable_chat_history"]

    @staticmethod
    @functools.cache
    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def get_active_config_or_default():
        logger.info("Method get_active_config_or_default started")
        env_helper = EnvHelper()
        config = ConfigHelper.get_default_config()
        if env_helper.LOAD_CONFIG_FROM_BLOB_STORAGE and storage_account:
            logger.info("Loading configuration from Blob Storage")

            try:
                # Check if config file exists
                storage_account.download_blob(CONFIG_FILE_NAME, container_name=CONFIG_CONTAINER_NAME)
                logger.info("Configuration file found in Blob Storage")
                default_config = config
                config_file = storage_account.download_blob(CONFIG_FILE_NAME, container_name=CONFIG_CONTAINER_NAME)
                config = json.loads(config_file)

                ConfigHelper._set_new_config_properties(config, default_config)
            except Exception:
                logger.info(
                    "Configuration file not found in Blob Storage, using default configuration"
                )

        logger.info("Method get_active_config_or_default ended")
        return Config(config)

    @staticmethod
    @functools.cache
    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def get_default_assistant_prompt():
        config = ConfigHelper.get_default_config()
        return config["prompts"]["answering_user_prompt"]

    @staticmethod
    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=log_result)
    def save_config_as_active(config):
        ConfigHelper.validate_config(config)
        if storage_account:
            storage_account.upload_blob(
                blob_name=CONFIG_FILE_NAME,
                data=json.dumps(config, indent=2),
                container_name=CONFIG_CONTAINER_NAME,
                overwrite=True,
                content_type="application/json",
            )
        ConfigHelper.get_active_config_or_default.cache_clear()

    @staticmethod
    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=log_result)
    def validate_config(config: dict):
        for document_processor in config.get("document_processors"):
            document_type = document_processor.get("document_type")
            unsupported_advanced_image_processing_file_type = (
                document_type not in ADVANCED_IMAGE_PROCESSING_FILE_TYPES
            )
            if (
                document_processor.get("use_advanced_image_processing")
                and unsupported_advanced_image_processing_file_type
            ):
                raise Exception(
                    f"Advanced image processing has not been enabled for document type {document_type}, as only {ADVANCED_IMAGE_PROCESSING_FILE_TYPES} file types are supported."
                )

    @staticmethod
    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def get_default_config():
        if ConfigHelper._default_config is None:
            env_helper = EnvHelper()

            config_file_path = os.path.join(os.path.dirname(__file__), "default.json")
            logger.info("Loading default config from %s", config_file_path)
            with open(config_file_path, encoding="utf-8") as f:
                ConfigHelper._default_config = json.loads(
                    Template(f.read()).substitute(
                        ORCHESTRATION_STRATEGY="semantic_kernel",
                        LOG_USER_INTERACTIONS=False,
                        LOG_TOKENS=False,
                        CONVERSATION_FLOW=env_helper.CONVERSATION_FLOW,
                    )
                )
                if env_helper.USE_ADVANCED_IMAGE_PROCESSING:
                    ConfigHelper._append_advanced_image_processors()

        return ConfigHelper._default_config

    @staticmethod
    @functools.cache
    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def get_default_contract_assistant():
        contract_file_path = os.path.join(
            os.path.dirname(__file__), "default_contract_assistant_prompt.txt"
        )
        contract_assistant = ""
        with open(contract_file_path, encoding="utf-8") as f:
            contract_assistant = f.readlines()

        return "".join([str(elem) for elem in contract_assistant])

    @staticmethod
    @functools.cache
    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def get_default_employee_assistant():
        employee_file_path = os.path.join(
            os.path.dirname(__file__), "default_employee_assistant_prompt.txt"
        )
        employee_assistant = ""
        with open(employee_file_path, encoding="utf-8") as f:
            employee_assistant = f.readlines()

        return "".join([str(elem) for elem in employee_assistant])

    @staticmethod
    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def clear_config():
        ConfigHelper._default_config = None
        ConfigHelper.get_active_config_or_default.cache_clear()

    @staticmethod
    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def _append_advanced_image_processors():
        image_file_types = ["jpeg", "jpg", "png", "tiff", "bmp"]
        ConfigHelper._remove_processors_for_file_types(image_file_types)
        ConfigHelper._default_config["document_processors"].extend(
            [
                {"document_type": file_type, "use_advanced_image_processing": True}
                for file_type in image_file_types
            ]
        )

    @staticmethod
    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def _remove_processors_for_file_types(file_types: list[str]):
        document_processors = ConfigHelper._default_config["document_processors"]
        document_processors = [
            document_processor
            for document_processor in document_processors
            if document_processor["document_type"] not in file_types
        ]
        ConfigHelper._default_config["document_processors"] = document_processors

    @staticmethod
    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def delete_config():
        if storage_account:
            storage_account.delete_blob(CONFIG_FILE_NAME, container_name=CONFIG_CONTAINER_NAME)
