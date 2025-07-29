from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from google.oauth2.service_account import Credentials
from redis.asyncio.client import Redis
from redis.exceptions import RedisError
from starlette.exceptions import HTTPException
from starlette.types import Lifespan, AppType
from sqlalchemy import MetaData
from typing import Optional
from maleo_foundation.client.manager import MaleoFoundationClientManager
from maleo_foundation.enums import BaseEnums
from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_foundation.models.transfers.general.token import (
    MaleoFoundationTokenGeneralTransfers,
)
from maleo_foundation.models.transfers.parameters.token import (
    MaleoFoundationTokenParametersTransfers,
)
from maleo_foundation.models.transfers.general.configurations import (
    Configurations,
    Loggers,
)
from maleo_foundation.models.transfers.general.credentials import MaleoCredentials
from maleo_foundation.models.transfers.general.settings import Settings
from maleo_foundation.managers.cache import CacheManagers
from maleo_foundation.managers.db import DatabaseManager
from maleo_foundation.managers.client.google.storage import GoogleCloudStorage
from maleo_foundation.managers.client.google.secret import GoogleSecretManager
from maleo_foundation.managers.middleware import MiddlewareManager
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.exceptions.request import BaseRequestExceptions
from maleo_foundation.utils.logging import (
    SimpleConfig,
    ApplicationLogger,
    CacheLogger,
    DatabaseLogger,
    MiddlewareLogger,
    RepositoryLogger,
    ServiceLogger,
)
from .credential import CredentialManager
from .configuration import ConfigurationManager


class ServiceManager:
    def __init__(
        self,
        db_metadata: MetaData,
        log_config: SimpleConfig,
        settings: Optional[Settings] = None,
    ):
        self._db_metadata = db_metadata  # * Declare DB Metadata
        self._log_config = log_config  # * Declare log config
        self._settings = (
            settings if settings is not None else Settings()  # type: ignore
        )  # * Initialize settings

        # * Disable google cloud logging if environment is local
        if self._settings.ENVIRONMENT == "local":
            self._log_config.google_cloud_logging = None

        # * Initialize Credential Manager
        self._credential_manager = CredentialManager(
            settings=self._settings, log_config=self._log_config
        )

        # * Initialize Configuration Manager
        self._configuration_manager = ConfigurationManager(
            settings=self._settings, credential_manager=self._credential_manager
        )

        self._load_keys()
        self._initialize_loggers()
        self._initialize_database()
        self._initialize_foundation()

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def log_config(self) -> SimpleConfig:
        return self._log_config

    @property
    def google_credentials(self) -> Credentials:
        return self._credential_manager.google_credentials

    @property
    def secret_manager(self) -> GoogleSecretManager:
        return self._credential_manager.secret_manager

    @property
    def maleo_credentials(self) -> MaleoCredentials:
        return self._credential_manager.maleo_credentials

    @property
    def configurations(self) -> Configurations:
        return self._configuration_manager.configurations

    def _load_keys(self) -> None:
        if self.settings.KEY_PASSWORD is not None:
            password = self.settings.KEY_PASSWORD
        else:
            password = self.secret_manager.get(name="maleo-key-password")

        if self.settings.PRIVATE_KEY is not None:
            private = self.settings.PRIVATE_KEY
        else:
            private = self.secret_manager.get(name="maleo-private-key")

        if self.settings.PUBLIC_KEY is not None:
            public = self.settings.PUBLIC_KEY
        else:
            public = self.secret_manager.get(name="maleo-public-key")

        self._keys = BaseGeneralSchemas.RSAKeys(
            password=password, private=private, public=public
        )

    @property
    def keys(self) -> BaseGeneralSchemas.RSAKeys:
        return self._keys

    def _initialize_loggers(self) -> None:
        application = ApplicationLogger(
            service_key=self.configurations.service.key, **self._log_config.model_dump()
        )
        cache = CacheLogger(
            service_key=self.configurations.service.key, **self._log_config.model_dump()
        )
        database = DatabaseLogger(
            service_key=self.configurations.service.key, **self._log_config.model_dump()
        )
        middleware = MiddlewareLogger(
            service_key=self.configurations.service.key, **self._log_config.model_dump()
        )
        repository = RepositoryLogger(
            service_key=self.configurations.service.key, **self._log_config.model_dump()
        )
        service = ServiceLogger(
            service_key=self.configurations.service.key, **self._log_config.model_dump()
        )
        self._loggers = Loggers(
            application=application,
            cache=cache,
            database=database,
            middleware=middleware,
            repository=repository,
            service=service,
        )

    @property
    def loggers(self) -> Loggers:
        return self._loggers

    async def _clear_cache(self) -> None:
        prefixes = [
            self.configurations.service.key,
            f"google-cloud-storage:{self.configurations.service.key}",
        ]
        for prefix in prefixes:
            async for key in self._redis.scan_iter(f"{prefix}*"):
                await self._redis.delete(key)

    async def check_redis_connection(self) -> bool:
        try:
            await self._redis.ping()
            self._loggers.cache.info("Redis connection check successful.")
            return True
        except RedisError as e:
            self._loggers.cache.error(
                f"Redis connection check failed: {e}", exc_info=True
            )
            return False

    async def initialize_cache(self) -> None:
        self._redis = Redis(
            host=self.configurations.cache.redis.host,
            port=self.configurations.cache.redis.port,
            db=self.configurations.cache.redis.db,
            password=self.configurations.cache.redis.password,
            decode_responses=self.configurations.cache.redis.decode_responses,
            health_check_interval=self.configurations.cache.redis.health_check_interval,
        )
        await self.check_redis_connection()
        self._cache = CacheManagers(redis=self._redis)
        await self._clear_cache()

    @property
    def redis(self) -> Redis:
        return self._redis

    @property
    def cache(self) -> CacheManagers:
        return self._cache

    def initialize_cloud_storage(self) -> None:
        environment = (
            BaseEnums.EnvironmentType.STAGING
            if self._settings.ENVIRONMENT == BaseEnums.EnvironmentType.LOCAL
            else self._settings.ENVIRONMENT
        )
        self._cloud_storage = GoogleCloudStorage(
            log_config=self._log_config,
            service_key=self._settings.SERVICE_KEY,
            bucket_name=f"maleo-suite-{environment}",
            credentials=self.google_credentials,
            redis=self._redis,
        )

    @property
    def cloud_storage(self) -> GoogleCloudStorage:
        return self._cloud_storage

    def _initialize_database(self) -> None:
        self._database = DatabaseManager(
            metadata=self._db_metadata,
            logger=self._loggers.database,
            url=self.configurations.database.url,
        )

    @property
    def database(self) -> DatabaseManager:
        return self._database

    def _initialize_foundation(self) -> None:
        self._foundation = MaleoFoundationClientManager(
            log_config=self._log_config, service_key=self._settings.SERVICE_KEY
        )

    @property
    def foundation(self) -> MaleoFoundationClientManager:
        return self._foundation

    @property
    def token(self) -> BaseTypes.OptionalString:
        payload = MaleoFoundationTokenGeneralTransfers.BaseEncodePayload(
            iss=None,
            sub=str(self.maleo_credentials.id),
            sr="administrator",
            u_i=self.maleo_credentials.id,
            u_uu=self.maleo_credentials.uuid,
            u_u=self.maleo_credentials.username,
            u_e=self.maleo_credentials.email,
            u_ut="service",
            o_i=None,
            o_uu=None,
            o_k=None,
            o_ot=None,
            uor=None,
            exp_in=1,
        )
        parameters = MaleoFoundationTokenParametersTransfers.Encode(
            key=self._keys.private, password=self._keys.password, payload=payload
        )
        result = self._foundation.services.token.encode(parameters=parameters)
        return result.data.token if result.success and result.data is not None else None

    def create_app(
        self,
        router: APIRouter,
        lifespan: Optional[Lifespan[AppType]] = None,
        version: str = "unknown",
    ) -> FastAPI:
        self._loggers.application.info("Creating FastAPI application")
        root_path = self._settings.ROOT_PATH
        self._app = FastAPI(
            title=self.configurations.service.name,
            version=version,
            lifespan=lifespan,  # type: ignore
            root_path=root_path,
        )
        self._loggers.application.info("FastAPI application created successfully")

        # * Add middleware(s)
        self._loggers.application.info("Configuring middlewares")
        self._middleware = MiddlewareManager(
            app=self._app,
            configurations=self.configurations.middleware,
            keys=self._keys,
            logger=self._loggers.middleware,
            maleo_foundation=self._foundation,
        )
        self._middleware.add_all()
        self._loggers.application.info("Middlewares added successfully")

        # * Add exception handler(s)
        self._loggers.application.info("Adding exception handlers")
        self._app.add_exception_handler(
            exc_class_or_status_code=RequestValidationError,
            handler=BaseRequestExceptions.validation_exception_handler,  # type: ignore
        )
        self._app.add_exception_handler(
            exc_class_or_status_code=HTTPException,
            handler=BaseRequestExceptions.http_exception_handler,  # type: ignore
        )
        self._loggers.application.info("Exception handlers added successfully")

        # * Include router
        self._loggers.application.info("Including routers")
        self._app.include_router(router)
        self._loggers.application.info("Routers included successfully")

        return self._app

    @property
    def app(self) -> FastAPI:
        return self._app

    async def dispose(self) -> None:
        self._loggers.application.info("Disposing service manager")
        if self._redis is not None:
            await self._redis.close()
        if self._database is not None:
            self._database.dispose()
        self._loggers.application.info("Service manager disposed successfully")
        if self._loggers is not None:
            self._loggers.application.info("Disposing logger")
            self._loggers.application.dispose()
            self._loggers.database.info("Disposing logger")
            self._loggers.database.dispose()
            self._loggers.middleware.info("Disposing logger")
            self._loggers.middleware.dispose()
