"""Auth routes."""

import logging
import sys

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from zmp_authentication_provider.auth.oauth2_keycloak import (
    KEYCLOAK_AUTH_ENDPOINT,
    KEYCLOAK_CLIENT_ID,
    KEYCLOAK_CLIENT_SECRET,
    KEYCLOAK_END_SESSION_ENDPOINT,
    KEYCLOAK_REDIRECT_URI,
    KEYCLOAK_TOKEN_ENDPOINT,
    KEYCLOAK_USER_ENDPOINT,
    TokenData,
    get_current_user,
    oauth2_auth_scheme,
)
from zmp_authentication_provider.exceptions import (
    AuthBackendException,
    AuthError,
)
from zmp_authentication_provider.setting import auth_default_settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/home", summary="Home page", response_class=HTMLResponse)
def home(request: Request):  # , csrf_token: str = Depends(csrf_scheme)):
    """Get home page."""
    # check the session_id in the cookie
    csrf_token = request.cookies.get(auth_default_settings.csrf_token_cookie_name)
    session_id = request.cookies.get(auth_default_settings.session_id_cookie_name)

    logger.debug(f"csrf_token: {csrf_token}")
    logger.debug(f"session_id: {session_id}")

    if csrf_token and session_id:
        user_info = request.session.get("user_info")
        if not user_info:
            request.session.clear()
            raise AuthBackendException(
                AuthError.SESSION_EXPIRED,
                code=401,
                details="Session data has been lost "
                "because the server has been restared."
                "Please login again",
            )
        else:
            username = user_info.get("preferred_username") if user_info else "Ooops!!"
            logger.debug(f"session_data: {username}")
            # TODO: redirect to the redirect_uri with the query params
            return HTMLResponse(content=f"<p>Hello, {username}!!</p>")
    else:
        # TODO: add the referer to the query params
        return RedirectResponse(
            url=f"{auth_default_settings.application_endpoint}/auth/login"
        )


@router.get(
    "/login",
    summary="API to login into the keyclaok using the browser",
    response_class=RedirectResponse,
)
def login():
    """Login."""
    # TODO: add the referer to the query params
    return RedirectResponse(
        url=f"{KEYCLOAK_AUTH_ENDPOINT}?response_type=code"
        f"&client_id={KEYCLOAK_CLIENT_ID}"
        f"&redirect_uri={KEYCLOAK_REDIRECT_URI}"
        f"&scope=openid profile email"
    )


@router.get(
    "/validate",
    summary="API to validate whether the user is logged in or not",
    response_class=RedirectResponse,
)
def validate(request: Request):
    """Validate whether the user is logged in or not."""
    # check the session_id in the cookie
    csrf_token = request.cookies.get(auth_default_settings.csrf_token_cookie_name)
    session_id = request.cookies.get(auth_default_settings.session_id_cookie_name)

    logger.debug(f"csrf_token: {csrf_token}")
    logger.debug(f"session_id: {session_id}")

    # for the redirect to the referer
    referer = request.headers.get("referer")
    referer = referer or "/"

    logger.debug(f"referer: {referer}")

    if csrf_token and session_id:
        user_info = request.session.get("user_info")
        if not user_info:
            request.session.clear()
            logger.error("Session data has been lost "
                "because the server has been restared."
                "Please login again",
            )
            return RedirectResponse(
                url=f"{KEYCLOAK_AUTH_ENDPOINT}?response_type=code"
                f"&client_id={KEYCLOAK_CLIENT_ID}"
                f"&state={csrf_token}{auth_default_settings.state_separator}{referer}"
                f"&redirect_uri={KEYCLOAK_REDIRECT_URI}"
                f"&scope=openid profile email"
                # NOTE: referer is not used in the keycloak
                # f"&referer={referer}"
            )
        else:
            username = user_info.get("preferred_username") if user_info else "Ooops!!"
            logger.debug(f"session_data: {username}")

            return RedirectResponse(url=f"{referer}")
    else:
        return RedirectResponse(
            url=f"{KEYCLOAK_AUTH_ENDPOINT}?response_type=code"
            f"&client_id={KEYCLOAK_CLIENT_ID}"
            f"&state={csrf_token}{auth_default_settings.state_separator}{referer}"
            f"&redirect_uri={KEYCLOAK_REDIRECT_URI}"
            f"&scope=openid profile email"
            # NOTE: referer is not used in the keycloak
            # f"&referer={referer}"
        )


@router.get(
    "/logout",
    summary="API to logout from the keyclaok",
    response_class=RedirectResponse,
)
def logout(
    request: Request,
    # csrf_token: str = Depends(csrf_scheme),
    # session_id: str = Depends(session_id_scheme)
):
    """Logout."""
    csrf_token = request.cookies.get(auth_default_settings.csrf_token_cookie_name)
    session_id = request.cookies.get(auth_default_settings.session_id_cookie_name)
    if not csrf_token or not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No csrf token in cookie and session id in cookie",
        )

    else:
        refresh_token = request.session.get("refresh_token")

        # if not session_id and not refresh_token:
        if refresh_token:
            data = {
                "client_id": KEYCLOAK_CLIENT_ID,
                "client_secret": KEYCLOAK_CLIENT_SECRET,
                "refresh_token": refresh_token,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            idp_response = requests.post(
                KEYCLOAK_END_SESSION_ENDPOINT,
                data=data,
                headers=headers,
                verify=auth_default_settings.http_client_ssl_verify,
            )  # verify=False: because of the SKCC self-signed certificate

            if idp_response.status_code != 204:
                raise AuthBackendException(
                    AuthError.OAUTH_IDP_ERROR,
                    details=f"Failed to logout.({idp_response.reason})",
                )

        request.session.clear()

        redirect_response = RedirectResponse(
            url=f"{auth_default_settings.application_endpoint}/auth/home"
        )
        redirect_response.delete_cookie(key="csrftoken")

        return redirect_response


@router.post("/oauth2/logout", summary="API to logout from the keyclaok only OAuth2")
def logout_only_oauth(
    refresh_token: str | None, access_token: str = Depends(oauth2_auth_scheme)
):
    """Logout only OAuth2."""
    data = {
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*"}
    idp_response = requests.post(
        KEYCLOAK_END_SESSION_ENDPOINT,
        data=data,
        headers=headers,
        verify=auth_default_settings.http_client_ssl_verify,
    )  # verify=False: because of the SKCC self-signed certificate

    if idp_response.status_code != 204:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details=f"Failed to logout.({idp_response.reason})",
        )

    return {"result": "success"}


@router.get("/oauth2/callback", summary="Keycloak OAuth2 callback for the redirect URI")
def callback(request: Request, code: str, state: str):
    """Keycloak OAuth2 callback for the redirect URI."""
    csrf_token = request.cookies.get(auth_default_settings.csrf_token_cookie_name)

    state = state.split(auth_default_settings.state_separator)
    received_csrf_token = state[0]
    referer = state[1]

    logger.debug(f"cookie csrftoken: {csrf_token}")
    logger.debug(f"state: {state}")
    logger.debug(f"received csrftoken: {received_csrf_token}")
    logger.debug(f"referer: {referer}")

    if received_csrf_token != csrf_token:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details=f"CSRF token mismatch.({received_csrf_token} != {csrf_token})",
        )

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": KEYCLOAK_REDIRECT_URI,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    idp_response = requests.post(
        KEYCLOAK_TOKEN_ENDPOINT,
        data=data,
        headers=headers,
        verify=auth_default_settings.http_client_ssl_verify,
    )  # verify=False: because of the SKCC self-signed certificate

    if idp_response.status_code != 200:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details=f"Failed to obtain token.({idp_response.reason})",
        )

    tokens = idp_response.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    # id_token = tokens.get("id_token")

    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    idp_response = requests.get(
        KEYCLOAK_USER_ENDPOINT,
        headers=headers,
        verify=auth_default_settings.http_client_ssl_verify,
    )  # verify=False: because of the SKCC self-signed certificate
    if idp_response.status_code != 200:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details=f"Failed to fetch user info.({idp_response.reason})",
        )
    user_info = idp_response.json()

    logger.debug(f"user_info: {user_info}")

    # because the max size of the cookie is 4kb, the session middleware saves the session data in the client side cookie in default
    # so, if the session data size is over than 4kb, the session data will be lost or occur the error in client side
    # request.session['access_token'] = access_token
    # request.session['id_token'] = id_token
    request.session["refresh_token"] = refresh_token
    request.session["user_info"] = user_info

    total_bytes = _get_size(request.session)

    if total_bytes > 4096:
        logger.debug(f"Total bytes: {total_bytes}")
        logger.warning(f"The session data size({total_bytes}) is over than 4kb.")
        raise AuthBackendException(
            AuthError.TOKEN_DATA_TOO_LARGE,
            details=f"The session data size is {total_bytes} bytes. It is over than 4kb.",
        )

    # If the same-site of cookie is 'lax', the cookie will be sent only if the request is same-site request
    # If the same-site of cookie is 'strict', the cookie will not be sent
    return RedirectResponse(
        # url=f"{auth_default_settings.application_endpoint}/auth/home"
        url=f"{referer}"
    )


def _get_size(obj, seen=None):
    """Recursively find the size of objects including nested objects."""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Mark as seen
    seen.add(obj_id)
    # Recursively add sizes of referred objects
    if isinstance(obj, dict):
        size += sum([_get_size(v, seen) for v in obj.values()])
        size += sum([_get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += _get_size(obj.__dict__, seen)
    elif isinstance(obj, list | tuple | set):
        size += sum([_get_size(i, seen) for i in obj])
    return size


@router.get("/users/me", summary="Get the current user info from IDP(Keycloak)")
def read_users_me(token: str = Depends(oauth2_auth_scheme)):
    """Get the current user info from IDP(Keycloak)."""
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    idp_response = requests.get(
        KEYCLOAK_USER_ENDPOINT,
        headers=headers,
        verify=auth_default_settings.http_client_ssl_verify,
    )  # verify=False: because of the SKCC self-signed certificate
    if idp_response.status_code != 200:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details=f"Failed to fetch user info: {idp_response.reason}",
        )
    return idp_response.json()


@router.get("/users/oauth_user", summary="Get the current user info from Token")
def read_oauth_user(oauth_user: TokenData = Depends(get_current_user)):
    """Get the current user info from Token."""
    return oauth_user
