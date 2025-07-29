import logging
from enum import IntEnum, StrEnum, Enum
from fastapi import responses


class BaseEnums:
    class EnvironmentType(StrEnum):
        LOCAL = "local"
        STAGING = "staging"
        PRODUCTION = "production"

    class ServiceType(StrEnum):
        BACKEND = "backend"
        FRONTEND = "frontend"

    class ServiceCategory(StrEnum):
        CORE = "core"
        AI = "ai"

    class ShortService(StrEnum):
        STUDIO = "studio"
        NEXUS = "nexus"
        TELEMETRY = "telemetry"
        METADATA = "metadata"
        IDENTITY = "identity"
        ACCESS = "access"
        WORKSHOP = "workshop"
        SOAPIE = "soapie"
        MEDIX = "medix"
        DICOM = "dicom"
        SCRIBE = "scribe"
        CDS = "cds"
        IMAGING = "imaging"
        MCU = "mcu"

    class Service(StrEnum):
        MALEO_STUDIO = "maleo-studio"
        MALEO_NEXUS = "maleo-nexus"
        MALEO_TELEMETRY = "maleo-telemetry"
        MALEO_METADATA = "maleo-metadata"
        MALEO_IDENTITY = "maleo-identity"
        MALEO_ACCESS = "maleo-access"
        MALEO_WORKSHOP = "maleo-workshop"
        MALEO_SOAPIE = "maleo-soapie"
        MALEO_MEDIX = "maleo-medix"
        MALEO_DICOM = "maleo-dicom"
        MALEO_SCRIBE = "maleo-scribe"
        MALEO_CDS = "maleo-cds"
        MALEO_IMAGING = "maleo-imaging"
        MALEO_MCU = "maleo-mcu"

    class StatusType(StrEnum):
        DELETED = "deleted"
        INACTIVE = "inactive"
        ACTIVE = "active"

    class UserType(StrEnum):
        REGULAR = "regular"
        PROXY = "proxy"
        SERVICE = "service"

    class SortOrder(StrEnum):
        ASC = "asc"
        DESC = "desc"

    class TokenType(StrEnum):
        REFRESH = "refresh"
        ACCESS = "access"

    class ExceptionType(StrEnum):
        TIMEOUT = "timeout"
        UNAUTHORIZED = "unauthorized"
        FORBIDDEN = "forbidden"
        NOT_FOUND = "not_found"
        VALIDATION = "validation"
        INTERNAL = "internal"
        UNAVAILABLE = "unavailable"

    class OperationOrigin(StrEnum):
        SERVICE = "service"
        CLIENT = "client"

    class ServiceOperationLayer(StrEnum):
        ROUTER = "router"
        CONTROLLER = "controller"
        SERVICE = "service"
        REPOSITORY = "repository"

    class ClientOperationLayer(StrEnum):
        CONTROLLER = "controller"
        SERVICE = "service"

    class OperationLayer(StrEnum):
        ROUTER = "router"
        CONTROLLER = "controller"
        SERVICE = "service"
        REPOSITORY = "repository"

    class ServiceOperationTarget(StrEnum):
        CACHE = "cache"
        DATABASE = "database"
        MICROSERVICE = "microservice"
        THIRD_PARTY = "third_party"
        INTERNAL = "internal"

    class ClientOperationTarget(StrEnum):
        CACHE = "cache"
        CONTROLLER = "controller"
        INTERNAL = "internal"

    class OperationTarget(StrEnum):
        CACHE = "cache"
        CONTROLLER = "controller"
        DATABASE = "database"
        INTERNAL = "internal"
        MICROSERVICE = "microservice"
        REPOSITORY = "repository"
        THIRD_PARTY = "third_party"

    class OperationType(StrEnum):
        CREATE = "create"
        READ = "read"
        UPDATE = "update"
        DELETE = "delete"

    class CreateType(StrEnum):
        CREATE = "create"
        RESTORE = "restore"

    class UpdateType(StrEnum):
        DATA = "data"
        STATUS = "status"

    class StatusUpdateType(StrEnum):
        ACTIVATE = "activate"
        DEACTIVATE = "deactivate"
        RESTORE = "restore"
        DELETE = "delete"

    class IdentifierType(StrEnum):
        ID = "id"
        UUID = "uuid"

    class ServiceControllerType(StrEnum):
        REST = "rest"
        MESSAGE = "message"

    class ClientControllerType(StrEnum):
        HTTP = "http"

    class ClientCategory(StrEnum):
        GOOGLE = "google"
        MALEO = "maleo"

    class KeyType(StrEnum):
        PRIVATE = "private"
        PUBLIC = "public"

    class KeyFormatType(Enum):
        BYTES = bytes
        STRING = str

    class RESTControllerResponseType(StrEnum):
        NONE = "none"
        HTML = "html"
        TEXT = "text"
        JSON = "json"
        REDIRECT = "redirect"
        STREAMING = "streaming"
        FILE = "file"

        def get_response_type(self) -> type[responses.Response]:
            """Returns the corresponding FastAPI Response type."""
            return {
                BaseEnums.RESTControllerResponseType.NONE: responses.Response,
                BaseEnums.RESTControllerResponseType.HTML: responses.HTMLResponse,
                BaseEnums.RESTControllerResponseType.TEXT: responses.PlainTextResponse,
                BaseEnums.RESTControllerResponseType.JSON: responses.JSONResponse,
                BaseEnums.RESTControllerResponseType.REDIRECT: responses.RedirectResponse,
                BaseEnums.RESTControllerResponseType.STREAMING: responses.StreamingResponse,
                BaseEnums.RESTControllerResponseType.FILE: responses.FileResponse,
            }.get(self, responses.Response)

    class LoggerType(StrEnum):
        APPLICATION = "application"
        CACHE = "cache"
        CLIENT = "client"
        DATABASE = "database"
        MIDDLEWARE = "middleware"
        REPOSITORY = "repository"
        SERVICE = "service"

    class LoggerLevel(IntEnum):
        CRITICAL = logging.CRITICAL
        FATAL = logging.FATAL
        ERROR = logging.ERROR
        WARNING = logging.WARNING
        WARN = logging.WARN
        INFO = logging.INFO
        DEBUG = logging.DEBUG
        NOTSET = logging.NOTSET

    class CacheLayer(StrEnum):
        CLIENT = "client"
        REPOSITORY = "repository"
        ROUTER = "router"

    class Expiration(IntEnum):
        EXP_15SC = int(15)
        EXP_30SC = int(30)
        EXP_1MN = int(1 * 60)
        EXP_5MN = int(5 * 60)
        EXP_10MN = int(10 * 60)
        EXP_15MN = int(15 * 60)
        EXP_30MN = int(30 * 60)
        EXP_1HR = int(1 * 60 * 60)
        EXP_6HR = int(6 * 60 * 60)
        EXP_12HR = int(12 * 60 * 60)
        EXP_1DY = int(1 * 24 * 60 * 60)
        EXP_3DY = int(3 * 24 * 60 * 60)
        EXP_1WK = int(1 * 7 * 24 * 60 * 60)
        EXP_2WK = int(2 * 7 * 24 * 60 * 60)
        EXP_1MO = int(1 * 30 * 24 * 60 * 60)
