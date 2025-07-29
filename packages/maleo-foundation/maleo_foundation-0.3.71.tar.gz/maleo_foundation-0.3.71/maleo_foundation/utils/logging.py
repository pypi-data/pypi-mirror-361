import logging
import os
from datetime import datetime
from google.cloud.logging import Client
from google.cloud.logging.handlers import CloudLoggingHandler
from google.oauth2.service_account import Credentials
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union
from maleo_foundation.enums import BaseEnums
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.loaders.credential.google import GoogleCredentialsLoader


class GoogleCloudLogging:
    def __init__(self, credentials_path: Optional[Union[Path, str]] = None) -> None:
        self._credentials = GoogleCredentialsLoader.load(
            credentials_path=credentials_path
        )
        self._client = Client(credentials=self._credentials)
        self._client.setup_logging()

    @property
    def credentials(self) -> Credentials:
        if self._credentials is None:
            raise ValueError("Credentials have not been initialized.")
        return self._credentials

    @property
    def client(self) -> Client:
        if self._client is None:
            raise ValueError("Client has not been initialized.")
        return self._client

    def dispose(self) -> None:
        if self._credentials is not None:
            self._credentials = None
        if self._client is not None:
            self._client = None

    def create_handler(self, name: str) -> CloudLoggingHandler:
        return CloudLoggingHandler(client=self._client, name=name)


class SimpleConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dir: str = Field(..., description="Log's directory")
    level: BaseEnums.LoggerLevel = Field(
        BaseEnums.LoggerLevel.INFO, description="Log's level"
    )
    google_cloud_logging: Optional[GoogleCloudLogging] = Field(
        default_factory=GoogleCloudLogging, description="Google cloud logging"
    )


class BaseLogger(logging.Logger):
    def __init__(
        self,
        dir: str,
        type: BaseEnums.LoggerType,
        service_key: BaseTypes.OptionalString = None,
        client_key: BaseTypes.OptionalString = None,
        level: BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
    ):
        self._type = type  # * Declare logger type

        # * Ensure service_key exists
        self._service_key = service_key or os.getenv("SERVICE_KEY")
        if self._service_key is None:
            raise ValueError(
                "SERVICE_KEY environment variable must be set if 'service_key' is set to None"
            )

        self._client_key = client_key  # * Declare client key

        # * Ensure client_key is valid if logger type is a client
        if self._type == BaseEnums.LoggerType.CLIENT and self._client_key is None:
            raise ValueError(
                "'client_key' parameter must be provided if 'logger_type' is 'client'"
            )

        # * Define logger name
        if self._type == BaseEnums.LoggerType.CLIENT:
            self._name = f"{self._service_key} - {self._type} - {self._client_key}"
        else:
            self._name = f"{self._service_key} - {self._type}"

        super().__init__(self._name, level)  # * Init the superclass's logger

        # * Clear existing handlers to prevent duplicates
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()

        # * Formatter for logs
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # * Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

        # * Google Cloud Logging handler (If enabled)
        if google_cloud_logging is not None:
            cloud_logging_handler = google_cloud_logging.create_handler(
                name=self._name.replace(" ", "")
            )
            self.addHandler(cloud_logging_handler)
        else:
            self.info("Cloud logging is not configured.")

        # * Define log directory
        if self._type == BaseEnums.LoggerType.CLIENT:
            log_dir = f"{self._type}/{self._client_key}"
        else:
            log_dir = f"{self._type}"
        self._log_dir = os.path.join(dir, log_dir)
        os.makedirs(self._log_dir, exist_ok=True)

        # * Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = os.path.join(self._log_dir, f"{timestamp}.log")

        # * File handler
        file_handler = logging.FileHandler(log_filename, mode="a")
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

    @property
    def type(self) -> str:
        return self._type

    @property
    def service(self) -> str:
        if self._service_key is None:
            raise ValueError("Service key has not been initialized.")
        return self._service_key

    @property
    def client(self) -> str:
        raise NotImplementedError()

    @property
    def identity(self) -> str:
        return self._name

    @property
    def location(self) -> str:
        return self._log_dir

    def dispose(self):
        """Dispose of the logger by removing all handlers."""
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()
        self.handlers.clear()


class ApplicationLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        service_key: BaseTypes.OptionalString = None,
        level: BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
    ):
        super().__init__(
            dir=dir,
            type=BaseEnums.LoggerType.APPLICATION,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
        )


class CacheLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        service_key: BaseTypes.OptionalString = None,
        level: BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
    ):
        super().__init__(
            dir=dir,
            type=BaseEnums.LoggerType.CACHE,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
        )


class ClientLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        client_key: str,
        service_key: BaseTypes.OptionalString = None,
        level: BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
    ):
        super().__init__(
            dir=dir,
            type=BaseEnums.LoggerType.CLIENT,
            service_key=service_key,
            client_key=client_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
        )


class DatabaseLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        service_key: BaseTypes.OptionalString = None,
        level=BaseEnums.LoggerLevel.INFO,
        google_cloud_logging=None,
    ):
        super().__init__(
            dir=dir,
            type=BaseEnums.LoggerType.DATABASE,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
        )


class MiddlewareLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        service_key: BaseTypes.OptionalString = None,
        level=BaseEnums.LoggerLevel.INFO,
        google_cloud_logging=None,
    ):
        super().__init__(
            dir=dir,
            type=BaseEnums.LoggerType.MIDDLEWARE,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
        )


class RepositoryLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        service_key: BaseTypes.OptionalString = None,
        level: BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
    ):
        super().__init__(
            dir=dir,
            type=BaseEnums.LoggerType.REPOSITORY,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
        )


class ServiceLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        service_key: BaseTypes.OptionalString = None,
        level: BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
    ):
        super().__init__(
            dir=dir,
            type=BaseEnums.LoggerType.SERVICE,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
        )
