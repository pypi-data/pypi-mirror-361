from fastapi import Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import HTTPConnection
from uuid import UUID
from maleo_foundation.constants import TOKEN_SCHEME
from maleo_foundation.authentication import (
    Credentials as RequestCredentials,
    User as RequestUser,
)
from maleo_foundation.models.transfers.general.authentication import (
    Authentication,
    Credentials,
    User,
)
from maleo_foundation.models.transfers.general.authorization import Authorization
from maleo_foundation.models.transfers.general.request import RequestContext
from .parser import parse_user_agent


def extract_operation_id(request: Request) -> UUID:
    return request.state.operation_id


def extract_authentication(request: Request) -> Authentication:
    # validate credentials
    request_credentials = request.auth
    if not isinstance(request_credentials, RequestCredentials):
        raise TypeError("'credentials' is not of type 'RequestCredentials'")
    credentials = Credentials.model_validate(request_credentials, from_attributes=True)
    # validate user
    request_user = request.user
    if not isinstance(request_user, RequestUser):
        raise TypeError("'user' is not of type 'RequestUser'")
    user = User.model_validate(request_user, from_attributes=True)
    return Authentication(credentials=credentials, user=user)


def extract_authorization(
    token: HTTPAuthorizationCredentials = Security(TOKEN_SCHEME),
) -> Authorization:
    return Authorization(scheme=token.scheme, credentials=token.credentials)


def extract_client_ip(conn: HTTPConnection) -> str:
    """Extract client IP with more robust handling of proxies"""
    # * Check for X-Forwarded-For header (common when behind proxy/load balancer)
    x_forwarded_for = conn.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # * The client's IP is the first one in the list
        ips = [ip.strip() for ip in x_forwarded_for.split(",")]
        return ips[0]

    # * Check for X-Real-IP header (used by some proxies)
    x_real_ip = conn.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip

    # * Fall back to direct client connection
    return conn.client.host if conn.client else "unknown"


def extract_request_context(request: Request) -> RequestContext:
    request_id = request.state.request_id
    requested_at = request.state.requested_at

    headers = request.headers

    ip_address = extract_client_ip(request)

    user_agent_string = headers.get("user-agent", "")
    user_agent = parse_user_agent(user_agent_string=user_agent_string)

    return RequestContext(
        request_id=request_id,
        requested_at=requested_at,
        method=request.method,
        url=request.url.path,
        ip_address=ip_address,
        is_internal=(
            None
            if ip_address == "unknown"
            else (
                ip_address.startswith("10.")
                or ip_address.startswith("192.168.")
                or ip_address.startswith("172.")
            )
        ),
        headers=headers.items(),
        path_params=None if not request.path_params else request.path_params,
        query_params=None if not request.query_params else str(request.query_params),
        user_agent=user_agent,
        referer=headers.get("referer"),
        origin=headers.get("origin"),
        host=headers.get("host"),
        forwarded_proto=headers.get("x-forwarded-proto"),
        language=headers.get("accept-language"),
    )
