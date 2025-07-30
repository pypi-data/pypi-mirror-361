import json
import re
import threading
import traceback
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Awaitable, Callable, Optional, Dict, List
from uuid import UUID, uuid4

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from maleo_foundation.enums import BaseEnums
from maleo_foundation.client.manager import MaleoFoundationClientManager
from maleo_foundation.models.schemas import BaseGeneralSchemas
from maleo_foundation.models.responses import BaseResponses
from maleo_foundation.models.transfers.general.authentication import Authentication
from maleo_foundation.models.transfers.general.operation import (
    OperationOrigin,
    OperationLayer,
    OperationTarget,
    OperationContext,
    OperationMetadata,
    OperationException,
    OperationTimestamps,
    OperationResult,
    Operation,
)
from maleo_foundation.models.transfers.general.service import ServiceContext
from maleo_foundation.models.transfers.general.settings import Settings
from maleo_foundation.models.transfers.general.token import (
    MaleoFoundationTokenGeneralTransfers,
)
from maleo_foundation.models.transfers.parameters.token import (
    MaleoFoundationTokenParametersTransfers,
)
from maleo_foundation.models.transfers.parameters.signature import (
    MaleoFoundationSignatureParametersTransfers,
)
from maleo_foundation.models.transfers.general.request import RequestContext
from maleo_foundation.models.transfers.general.response import ResponseContext
from maleo_foundation.utils.extractor import (
    extract_authentication,
    extract_request_context,
)
from maleo_foundation.utils.logging import MiddlewareLogger

RequestProcessor = Callable[[Request], Awaitable[Optional[Response]]]
ResponseProcessor = Callable[[Response], Awaitable[Response]]


class RateLimiter:
    """Thread-safe rate limiter with automatic cleanup."""

    def __init__(
        self,
        limit: int,
        window: timedelta,
        ip_timeout: timedelta,
        cleanup_interval: timedelta,
    ):
        self.limit = limit
        self.window = window
        self.ip_timeout = ip_timeout
        self.cleanup_interval = cleanup_interval
        self._requests: Dict[str, List[datetime]] = defaultdict(list)
        self._last_seen: Dict[str, datetime] = {}
        self._last_cleanup = datetime.now()
        self._lock = threading.RLock()

    def is_rate_limited(self, request_context: RequestContext) -> bool:
        """Check if client IP is rate limited and record the request."""
        with self._lock:
            now = datetime.now()
            client_ip = request_context.ip_address
            self._last_seen[client_ip] = now

            # Remove old requests outside the window
            self._requests[client_ip] = [
                timestamp
                for timestamp in self._requests[client_ip]
                if now - timestamp <= self.window
            ]

            # Check rate limit
            if len(self._requests[client_ip]) >= self.limit:
                return True

            # Record this request
            self._requests[client_ip].append(now)
            return False

    def cleanup_old_data(self) -> None:
        """Clean up old request data to prevent memory growth."""
        now = datetime.now()
        if now - self._last_cleanup <= self.cleanup_interval:
            return

        with self._lock:
            inactive_ips = []

            for ip in list(self._requests.keys()):
                # Remove IPs with empty request lists
                if not self._requests[ip]:
                    inactive_ips.append(ip)
                    continue

                # Remove IPs that haven't been active recently
                last_active = self._last_seen.get(ip, datetime.min)
                if now - last_active > self.ip_timeout:
                    inactive_ips.append(ip)

            # Clean up inactive IPs
            for ip in inactive_ips:
                self._requests.pop(ip, None)
                self._last_seen.pop(ip, None)

            self._last_cleanup = now


class ResponseBuilder:
    """Handles response building and header management."""

    def __init__(
        self,
        keys: BaseGeneralSchemas.RSAKeys,
        maleo_foundation: MaleoFoundationClientManager,
    ):
        self.keys = keys
        self.maleo_foundation = maleo_foundation

    def _add_signature_header(
        self,
        operation_id: UUID,
        request_id: UUID,
        method: str,
        url: str,
        requested_at: datetime,
        responded_at: datetime,
        process_time: float,
        response: Response,
    ) -> None:
        """Generate and add signature header."""
        message = (
            f"{str(operation_id)}|"
            f"{str(request_id)}"
            f"{method}|"
            f"{url}|"
            f"{requested_at.isoformat()}|"
            f"{responded_at.isoformat()}|"
            f"{str(process_time)}|"
        )

        sign_parameters = MaleoFoundationSignatureParametersTransfers.Sign(
            key=self.keys.private, password=self.keys.password, message=message
        )

        sign_result = self.maleo_foundation.services.signature.sign(
            parameters=sign_parameters
        )
        if sign_result.success and sign_result.data is not None:
            response.headers["X-Signature"] = sign_result.data.signature

    def _should_regenerate_auth(
        self,
        request_context: RequestContext,
        authentication: Authentication,
        response: Response,
    ) -> bool:
        """Check if authorization should be regenerated."""
        if authentication.credentials.token is not None:
            return (
                authentication.user.is_authenticated
                and authentication.credentials.token.type == BaseEnums.TokenType.REFRESH
                and 200 <= response.status_code < 300
                and "logout" not in request_context.url
            )
        return False

    def _add_new_authorization_header(
        self,
        request_context: RequestContext,
        authentication: Authentication,
        response: Response,
    ) -> None:
        """Add new authorization header for refresh tokens."""
        if not self._should_regenerate_auth(request_context, authentication, response):
            return

        if authentication.credentials.token is None:
            return

        payload = MaleoFoundationTokenGeneralTransfers.BaseEncodePayload.model_validate(
            authentication.credentials.token.payload.model_dump()
        )

        parameters = MaleoFoundationTokenParametersTransfers.Encode(
            key=self.keys.private, password=self.keys.password, payload=payload
        )

        result = self.maleo_foundation.services.token.encode(parameters=parameters)
        if result.success and result.data is not None:
            response.headers["X-New-Authorization"] = result.data.token

    def add_response_headers(
        self,
        operation_id: UUID,
        request_context: RequestContext,
        authentication: Authentication,
        response: Response,
        responded_at: datetime,
        process_time: float,
    ) -> Response:
        """Add custom headers to response."""
        # Basic headers
        response.headers["X-Operation-Id"] = str(operation_id)
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-Id"] = str(request_context.request_id)
        response.headers["X-Requested-At"] = request_context.requested_at.isoformat()
        response.headers["X-Responded-At"] = responded_at.isoformat()

        # Add signature header
        self._add_signature_header(
            operation_id=operation_id,
            request_id=request_context.request_id,
            method=request_context.method,
            url=request_context.url,
            requested_at=request_context.requested_at,
            responded_at=responded_at,
            process_time=process_time,
            response=response,
        )

        # Add new authorization header if needed
        self._add_new_authorization_header(request_context, authentication, response)

        return response


class BaseMiddleware(BaseHTTPMiddleware):
    """Base middleware with rate limiting, logging, and response enhancement."""

    def __init__(
        self,
        app: ASGIApp,
        settings: Settings,
        keys: BaseGeneralSchemas.RSAKeys,
        logger: MiddlewareLogger,
        maleo_foundation: MaleoFoundationClientManager,
        limit: int = 10,
        window: int = 1,
        cleanup_interval: int = 60,
        ip_timeout: int = 300,
    ):
        super().__init__(app)

        self._settings = settings
        self._logger = logger

        # Core components
        self.rate_limiter = RateLimiter(
            limit=limit,
            window=timedelta(seconds=window),
            ip_timeout=timedelta(seconds=ip_timeout),
            cleanup_interval=timedelta(seconds=cleanup_interval),
        )
        self.response_builder = ResponseBuilder(keys, maleo_foundation)

        # define service_context
        self.service_context = ServiceContext(
            key=self._settings.SERVICE_KEY, environment=self._settings.ENVIRONMENT
        )

        # define operation context
        self.operation_context = OperationContext(
            origin=OperationOrigin(
                type=BaseEnums.OperationOrigin.SERVICE, properties=None
            ),
            layer=OperationLayer(
                type=BaseEnums.OperationLayer.MIDDLEWARE, properties=None
            ),
            target=OperationTarget(
                type=BaseEnums.OperationTarget.INTERNAL, properties=None
            ),
        )

    def _build_operation_metadata(
        self, request_context: RequestContext
    ) -> OperationMetadata:
        operation_type = BaseEnums.OperationType.OTHER
        create_type = None
        update_type = None
        status_update_type = None

        if request_context.method == "POST":
            operation_type = BaseEnums.OperationType.CREATE
            if request_context.url.endswith("/restore"):
                create_type = BaseEnums.CreateType.RESTORE
            else:
                create_type = BaseEnums.CreateType.CREATE
        elif request_context.method == "GET":
            operation_type = BaseEnums.OperationType.READ
        elif request_context.method in ["PATCH", "PUT"]:
            operation_type = BaseEnums.OperationType.UPDATE
            if request_context.method == "PUT":
                update_type = BaseEnums.UpdateType.DATA
            elif request_context.method == "PATCH":
                if request_context.url.endswith("/status"):
                    update_type = BaseEnums.UpdateType.STATUS
                    if request_context.query_params is not None:
                        match = re.search(
                            r"[?&]action=([^&]+)", request_context.query_params
                        )
                        if match:
                            try:
                                status_update_type = BaseEnums.StatusUpdateType(
                                    match.group(1)
                                )
                            except Exception:
                                pass
                else:
                    update_type = BaseEnums.UpdateType.DATA
        elif request_context.method == "DELETE":
            operation_type = BaseEnums.OperationType.DELETE

        metadata = OperationMetadata(
            type=operation_type,
            create_type=create_type,
            update_type=update_type,
            status_update_type=status_update_type,
        )

        return metadata

    def _log_operation(
        self,
        operation: Operation,
        log_level: BaseEnums.LogLevel = BaseEnums.LogLevel.INFO,
    ) -> None:
        exc_info = (
            log_level is BaseEnums.LogLevel.FATAL
            or log_level is BaseEnums.LogLevel.ERROR
            or log_level is BaseEnums.LogLevel.CRITICAL
        )

        self._logger.log(int(log_level), operation.to_log_string(), exc_info=exc_info)

        return None

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Main middleware dispatch method."""
        # Setup
        self.rate_limiter.cleanup_old_data()

        # Assign operation id
        operation_id = request.headers.get("X-Operation-Id", None)
        if operation_id is None:
            operation_id = uuid4()
        else:
            operation_id = UUID(operation_id)
        request.state.operation_id = operation_id

        # Assign request id and timestamp
        request.state.request_id = uuid4()
        request.state.requested_at = datetime.now(tz=timezone.utc)

        # Extract and assign request context
        request_context = extract_request_context(request)
        request.state.request_context = request_context

        # Extract authentication
        authentication = extract_authentication(request=request)

        started_at = datetime.now(tz=timezone.utc)

        # Rate limiting check
        if self.rate_limiter.is_rate_limited(request_context):
            finished_at = datetime.now(tz=timezone.utc)
            operation_summary = "Rate limit exceeded for the request"
            # define operation timestamps
            operation_timestamps = OperationTimestamps(
                started_at=started_at,
                finished_at=finished_at,
                duration=(finished_at - started_at).total_seconds(),
            )
            operation_exception = OperationException(
                type=BaseEnums.ExceptionType.RATE_LIMIT,
                raw="Rate limit exceeded",
                traceback=[],
            )
            content = BaseResponses.RateLimitExceeded().model_dump()  # type: ignore
            operation_result = OperationResult.model_validate(content)
            response = JSONResponse(
                content=content,
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )
            return self._build_final_response(
                operation_id=operation_id,
                operation_summary=operation_summary,
                request_context=request_context,
                authentication=authentication,
                operation_timestamps=operation_timestamps,
                operation_exception=operation_exception,
                operation_result=operation_result,
                response=response,
                log_level=BaseEnums.LogLevel.ERROR,
            )

        try:
            # Main request processing
            response = await call_next(request)
            finished_at = datetime.now(tz=timezone.utc)
            operation_summary = "Successfully processed the request"
            # define operation timestamps
            operation_timestamps = OperationTimestamps(
                started_at=started_at,
                finished_at=finished_at,
                duration=(finished_at - started_at).total_seconds(),
            )
            return self._build_final_response(
                operation_id=operation_id,
                operation_summary=operation_summary,
                request_context=request_context,
                authentication=authentication,
                operation_timestamps=operation_timestamps,
                operation_result=None,
                operation_exception=None,
                response=response,
            )

        except Exception as e:
            finished_at = datetime.now(tz=timezone.utc)
            operation_summary = "Unexpected error occured for the request"
            # define operation timestamps
            operation_timestamps = OperationTimestamps(
                started_at=started_at,
                finished_at=finished_at,
                duration=(finished_at - started_at).total_seconds(),
            )
            operation_exception = OperationException(
                type=BaseEnums.ExceptionType.INTERNAL,
                raw=str(e),
                traceback=traceback.format_exc().splitlines(),
            )
            content = (BaseResponses.ServerError(other=str(e)).model_dump(),)  # type: ignore
            operation_result = OperationResult.model_validate(content)
            response = JSONResponse(
                content=content,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            return self._build_final_response(
                operation_id=operation_id,
                operation_summary=operation_summary,
                request_context=request_context,
                authentication=authentication,
                operation_timestamps=operation_timestamps,
                operation_exception=operation_exception,
                operation_result=operation_result,
                response=response,
                log_level=BaseEnums.LogLevel.ERROR,
            )

    def _build_final_response(
        self,
        operation_id: UUID,
        operation_summary: str,
        request_context: RequestContext,
        authentication: Authentication,
        operation_timestamps: OperationTimestamps,
        operation_exception: Optional[OperationException],
        operation_result: Optional[OperationResult],
        response: Response,
        log_level: BaseEnums.LogLevel = BaseEnums.LogLevel.INFO,
    ) -> Response:
        """Build final response with headers and logging."""
        # define operation metadata
        operation_metadata = self._build_operation_metadata(
            request_context=request_context
        )

        # define result
        if operation_result is None:
            if isinstance(response, JSONResponse):
                try:
                    data = json.loads(response.body.decode())  # type: ignore
                    operation_result = OperationResult.model_validate(data)
                except Exception:
                    pass

        # define response-related timestamps
        responded_at = datetime.now(tz=timezone.utc)
        process_time = (responded_at - request_context.requested_at).total_seconds()

        # Add headers
        response = self.response_builder.add_response_headers(
            operation_id,
            request_context,
            authentication,
            response,
            responded_at,
            process_time,
        )

        # Define response context
        response_context = ResponseContext(
            responded_at=responded_at,
            process_time=process_time,
            headers=response.headers.items(),
        )

        # Define operation
        operation = Operation(
            operation_id=operation_id,
            summary=operation_summary,
            request_context=request_context,
            authentication=authentication,
            authorization=None,
            service=self.service_context,
            timestamps=operation_timestamps,
            context=self.operation_context,
            metadata=operation_metadata,
            exception=operation_exception,
            arguments=None,
            result=operation_result,
            response_context=response_context,
        )

        self._log_operation(operation=operation, log_level=log_level)

        return response


def add_base_middleware(
    app: FastAPI,
    settings: Settings,
    keys: BaseGeneralSchemas.RSAKeys,
    logger: MiddlewareLogger,
    maleo_foundation: MaleoFoundationClientManager,
    limit: int = 10,
    window: int = 1,
    cleanup_interval: int = 60,
    ip_timeout: int = 300,
) -> None:
    """
    Add Base middleware to the FastAPI application.

    Args:
        app:FastAPI application instance
        keys:RSA keys for signing and token generation
        logger:Middleware logger instance
        maleo_foundation:Client manager for foundation services
        allow_origins:CORS allowed origins
        allow_methods:CORS allowed methods
        allow_headers:CORS allowed headers
        allow_credentials:CORS allow credentials flag
        limit:Request count limit per window
        window:Time window for rate limiting (seconds)
        cleanup_interval:Cleanup interval for old IP data (seconds)
        ip_timeout:IP timeout after last activity (seconds)

    Example:
        ```python
        add_base_middleware(
            app=app,
            keys=rsa_keys,
            logger=middleware_logger,
            maleo_foundation=client_manager,
            limit=10,
            window=1,
            cleanup_interval=60,
            ip_timeout=300
        )
        ```
    """
    app.add_middleware(
        BaseMiddleware,
        settings=settings,
        keys=keys,
        logger=logger,
        maleo_foundation=maleo_foundation,
        limit=limit,
        window=window,
        cleanup_interval=cleanup_interval,
        ip_timeout=ip_timeout,
    )
