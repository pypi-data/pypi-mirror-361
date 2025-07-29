from datetime import datetime, timezone
from functools import wraps
from httpx import RequestError
from pydantic import ValidationError
from typing import Optional
from maleo_foundation.enums import BaseEnums
from maleo_foundation.models.transfers.general.request import RequestContext
from maleo_foundation.models.transfers.results.client.service import (
    BaseClientServiceResultsTransfers,
)
from maleo_foundation.utils.logging import BaseLogger


class BaseClientExceptions:
    @staticmethod
    def _exception_handler(
        layer: BaseEnums.OperationLayer,
        resource: str,
        operation: BaseEnums.OperationType,
        summary: str,
        e: Exception,
        exception: BaseEnums.ExceptionType,
        category: str,
        description: str,
        target: Optional[BaseEnums.OperationTarget] = None,
        environment: Optional[BaseEnums.EnvironmentType] = None,
        create_type: Optional[BaseEnums.CreateType] = None,
        update_type: Optional[BaseEnums.UpdateType] = None,
        status_update_type: Optional[BaseEnums.StatusUpdateType] = None,
        logger: Optional[BaseLogger] = None,
        fail_result_class: type[
            BaseClientServiceResultsTransfers.Fail
        ] = BaseClientServiceResultsTransfers.Fail,
        request_context: Optional[RequestContext] = None,
    ) -> BaseClientServiceResultsTransfers.Fail:
        if logger:
            log_string = f"{category} occurred while {summary}: '{str(e)}'"
            if request_context is not None:
                log_string = (
                    f"Request | ID: {request_context.request_id} - {log_string}"
                )
            logger.error(
                log_string,
                exc_info=True,
            )
        return fail_result_class(
            success=False,
            exception=exception,
            timestamp=datetime.now(timezone.utc),
            origin=BaseEnums.OperationOrigin.CLIENT,
            layer=layer,
            target=target,
            environment=environment,
            resource=resource,
            operation=operation,
            create_type=create_type,
            update_type=update_type,
            status_update_type=status_update_type,
            message=f"Failed {summary}",
            description=description,
            data=None,
            metadata=None,
            other=category,
        )

    @staticmethod
    def async_exception_handler(
        layer: BaseEnums.OperationLayer,
        resource: str,
        operation: BaseEnums.OperationType,
        summary: str,
        target: Optional[BaseEnums.OperationTarget] = None,
        environment: Optional[BaseEnums.EnvironmentType] = None,
        create_type: Optional[BaseEnums.CreateType] = None,
        update_type: Optional[BaseEnums.UpdateType] = None,
        status_update_type: Optional[BaseEnums.StatusUpdateType] = None,
        logger: Optional[BaseLogger] = None,
        fail_result_class: type[
            BaseClientServiceResultsTransfers.Fail
        ] = BaseClientServiceResultsTransfers.Fail,
    ):
        """Decorator to handle exceptions consistently for async operation functions."""

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Search for RequestContext in args and kwargs
                request_context: Optional[RequestContext] = None
                for arg in list(args) + list(kwargs.values()):
                    if isinstance(arg, RequestContext):
                        request_context = arg
                        break
                try:
                    return await func(*args, **kwargs)
                except ValidationError as e:
                    return BaseClientExceptions._exception_handler(
                        layer=layer,
                        resource=resource,
                        operation=operation,
                        summary=summary,
                        e=e,
                        exception=BaseEnums.ExceptionType.VALIDATION,
                        category="Validation error",
                        description=f"A validation error occurred while {operation}. Please try again later or contact administrator.",
                        target=target,
                        environment=environment,
                        create_type=create_type,
                        update_type=update_type,
                        status_update_type=status_update_type,
                        logger=logger,
                        fail_result_class=fail_result_class,
                        request_context=request_context,
                    )
                except RequestError as e:
                    return BaseClientExceptions._exception_handler(
                        layer=layer,
                        resource=resource,
                        operation=operation,
                        summary=summary,
                        e=e,
                        exception=BaseEnums.ExceptionType.UNAVAILABLE,
                        category="Request error",
                        description=f"A request error occurred while {operation}. Please try again later or contact administrator.",
                        target=target,
                        environment=environment,
                        create_type=create_type,
                        update_type=update_type,
                        status_update_type=status_update_type,
                        logger=logger,
                        fail_result_class=fail_result_class,
                        request_context=request_context,
                    )
                except Exception as e:
                    return BaseClientExceptions._exception_handler(
                        layer=layer,
                        resource=resource,
                        operation=operation,
                        summary=summary,
                        e=e,
                        exception=BaseEnums.ExceptionType.INTERNAL,
                        category="Internal processing error",
                        description=f"An unexpected error occurred while {operation}. Please try again later or contact administrator.",
                        target=target,
                        environment=environment,
                        create_type=create_type,
                        update_type=update_type,
                        status_update_type=status_update_type,
                        logger=logger,
                        fail_result_class=fail_result_class,
                        request_context=request_context,
                    )

            return wrapper

        return decorator

    @staticmethod
    def sync_exception_handler(
        layer: BaseEnums.OperationLayer,
        resource: str,
        operation: BaseEnums.OperationType,
        summary: str,
        target: Optional[BaseEnums.OperationTarget] = None,
        environment: Optional[BaseEnums.EnvironmentType] = None,
        create_type: Optional[BaseEnums.CreateType] = None,
        update_type: Optional[BaseEnums.UpdateType] = None,
        status_update_type: Optional[BaseEnums.StatusUpdateType] = None,
        logger: Optional[BaseLogger] = None,
        fail_result_class: type[
            BaseClientServiceResultsTransfers.Fail
        ] = BaseClientServiceResultsTransfers.Fail,
    ):
        """Decorator to handle exceptions consistently for sync operation functions."""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Search for RequestContext in args and kwargs
                request_context: Optional[RequestContext] = None
                for arg in list(args) + list(kwargs.values()):
                    if isinstance(arg, RequestContext):
                        request_context = arg
                        break
                try:
                    return func(*args, **kwargs)
                except ValidationError as e:
                    return BaseClientExceptions._exception_handler(
                        layer=layer,
                        resource=resource,
                        operation=operation,
                        summary=summary,
                        e=e,
                        exception=BaseEnums.ExceptionType.VALIDATION,
                        category="Validation error",
                        description=f"A validation error occurred while {operation}. Please try again later or contact administrator.",
                        target=target,
                        environment=environment,
                        create_type=create_type,
                        update_type=update_type,
                        status_update_type=status_update_type,
                        logger=logger,
                        fail_result_class=fail_result_class,
                        request_context=request_context,
                    )
                except RequestError as e:
                    return BaseClientExceptions._exception_handler(
                        layer=layer,
                        resource=resource,
                        operation=operation,
                        summary=summary,
                        e=e,
                        exception=BaseEnums.ExceptionType.UNAVAILABLE,
                        category="Request error",
                        description=f"A request error occurred while {operation}. Please try again later or contact administrator.",
                        target=target,
                        environment=environment,
                        create_type=create_type,
                        update_type=update_type,
                        status_update_type=status_update_type,
                        logger=logger,
                        fail_result_class=fail_result_class,
                        request_context=request_context,
                    )
                except Exception as e:
                    return BaseClientExceptions._exception_handler(
                        layer=layer,
                        resource=resource,
                        operation=operation,
                        summary=summary,
                        e=e,
                        exception=BaseEnums.ExceptionType.INTERNAL,
                        category="Internal processing error",
                        description=f"An unexpected error occurred while {operation}. Please try again later or contact administrator.",
                        target=target,
                        environment=environment,
                        create_type=create_type,
                        update_type=update_type,
                        status_update_type=status_update_type,
                        logger=logger,
                        fail_result_class=fail_result_class,
                        request_context=request_context,
                    )

            return wrapper

        return decorator
