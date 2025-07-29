import json
import os
from functools import wraps
from urllib.parse import quote

import cachetools.func
import flask
import requests
from cachetools import TTLCache, cached
from furl import furl
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .ratelimit import RateLimitError, rate_limit

AUTH_URI = os.environ.get("AUTH_URI", "localhost:5000/auth")
AUTH_URL = os.environ.get("AUTH_URL", AUTH_URI)
STICKY_AUTH_URL = os.environ.get("STICKY_AUTH_URL", AUTH_URL)

TOKEN_NAME = os.environ.get("TOKEN_NAME", "middle_auth_token")
CACHE_MAXSIZE = int(os.environ.get("TOKEN_CACHE_MAXSIZE", "1024"))
CACHE_TTL = int(os.environ.get("TOKEN_CACHE_TTL", "300"))

SKIP_CACHE_LIMIT = int(os.environ.get("TOKEN_CACHE_SKIP_LIMIT", "20"))
SKIP_CACHE_WINDOW_SEC = int(os.environ.get("TOKEN_CACHE_SKIP_WINDOW_SEC", "300"))

AUTH_DISABLED = os.environ.get("AUTH_DISABLED", "false") == "true"
AUTH_DEBUG = os.environ.get("AUTH_DEBUG", "false") == "true"
DEBUG_OVERRIDE_DATASET_LOOKUP = os.environ.get("DEBUG_OVERRIDE_DATASET_LOOKUP", None)

MY_PERMISSION_URL = os.environ.get(
    "MIDDLE_AUTH_MY_PERMISSION_URL", "/api/v1/user/cache"
)

PERMISSIONS_KEY = "permissions_v2"
PERMISSIONS_KEY_IGNORE_TOS = "permissions_v2_ignore_tos"


retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])

session = requests.Session()
session.mount("https://" + AUTH_URI, HTTPAdapter(max_retries=retries))


def debug_print(str):
    if AUTH_DEBUG:
        print(str)

_permission_lookup_override = None


def setPermissionLookupOverride(func):
    global _permission_lookup_override
    _permission_lookup_override = func


class AuthorizationError(Exception):
    pass

class MACAuthorizationError(Exception):
    def __init__(self, http_status, api_code, msg=None, data=None):
        super().__init__(self, msg)
        self.http_status = http_status
        self.api_code = api_code
        self.msg = msg
        self.data = data

    def to_response(self):
        res = {"error": self.api_code}

        if self.msg is not None:
            res["message"] = self.msg

        if self.data is not None:
            res["data"] = self.data

        response = flask.jsonify(res)
        response.status_code = self.http_status
        return response

def get_usernames(user_ids, token=None):
    if AUTH_DISABLED:
        return []

    if token is None:
        raise ValueError("missing token")
    if len(user_ids):
        users_request = session.get(
            f"https://{AUTH_URL}/api/v1/username?id={','.join(map(str, user_ids))}",
            headers={"authorization": "Bearer " + token},
            timeout=5,
        )

        if users_request.status_code in [401, 403]:
            raise AuthorizationError(users_request.text)
        elif users_request.status_code == 200:
            id_to_name = {x["id"]: x["name"] for x in users_request.json()}
            return [id_to_name[x] for x in user_ids]
        else:
            raise RuntimeError("get_usernames request failed")
    else:
        return []


token_to_user_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)

user_id_to_user_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)


@cached(cache=token_to_user_cache)
def user_cache_http(token):
    user_request = session.get(
        f"https://{AUTH_URL}{MY_PERMISSION_URL}",
        headers={"authorization": "Bearer " + token},
    )
    if user_request.status_code == 200:
        return user_request.json()


@cached(cache=user_id_to_user_cache)
def user_id_to_user_cache_http(user_id, service_token=None):
    token = (
        service_token
        if service_token
        else flask.current_app.config.get("AUTH_TOKEN", "")
    )
    user_request = session.get(
        f"https://{AUTH_URL}/api/v1/user/{user_id}/permissions",
        headers={"authorization": "Bearer " + token},
    )
    if user_request.status_code == 200:
        return user_request.json()


@rate_limit(limit_args=[0], limit=SKIP_CACHE_LIMIT, window_sec=SKIP_CACHE_WINDOW_SEC)
def clear_user_cache_maybe(token):
    token_to_user_cache.pop((token,), None)


def get_user_cache(token):
    lookup_function = (
        _permission_lookup_override if _permission_lookup_override else user_cache_http
    )
    return lookup_function(token)


@cachetools.func.ttl_cache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
def is_root_public(table_id, root_id, token):
    debug_print(f"is_root_public({table_id}, {root_id}, token_hidden)")
    if root_id is None:
        debug_print("is_root_public: no root_id")
        return False

    if AUTH_DISABLED:
        return True

    url = f"https://{AUTH_URL}/api/v1/table/{table_id}/root/{root_id}/is_public"

    req = session.get(url, headers={"authorization": "Bearer " + token}, timeout=5)

    if req.status_code == 200:
        res = req.json()
        debug_print(f"is_root_public: res - {res}")
        return res
    else:
        raise RuntimeError("is_root_public request failed")


@cachetools.func.ttl_cache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
def are_roots_public(table_id, root_ids, token):
    if type(root_ids) is not frozenset or len(root_ids) == 0:
        return False

    if AUTH_DISABLED:
        return True

    url = f"https://{AUTH_URL}/api/v1/table/{table_id}/root_all_public"
    headers = {"Content-type": "application/json", "authorization": "Bearer " + token}
    req = session.post(
        url, headers=headers, data=json.dumps(list(root_ids)), timeout=5
    )  # list(root_ids)

    if req.status_code == 200:
        return req.json()
    else:
        raise RuntimeError("is_root_public request failed")


@cachetools.func.ttl_cache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
def table_has_public(table_id, token):
    if AUTH_DISABLED:
        return True

    url = f"https://{AUTH_URL}/api/v1/table/{table_id}/has_public"

    req = session.get(url, headers={"authorization": "Bearer " + token}, timeout=5)
    if req.status_code == 200:
        return req.json()
    else:
        raise RuntimeError("has_public request failed")


@cachetools.func.ttl_cache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
def dataset_from_table_id(service_namespace, table_id, token):
    if DEBUG_OVERRIDE_DATASET_LOOKUP is not None:
        return DEBUG_OVERRIDE_DATASET_LOOKUP
    url = f"https://{AUTH_URL}/api/v1/service/{service_namespace}/table/{table_id}/dataset"
    req = session.get(url, headers={"authorization": "Bearer " + token}, timeout=5)
    if req.status_code == 200:
        return req.json()
    else:
        raise RuntimeError(
            f"failed to lookup dataset for service {service_namespace} & table_id: {table_id}: status code {req.status_code}. content: {req.content}"
        )

# some helper code surrounding dataset_from_table_id for use by the decorators 
def dataset_from_table_id_from_request(table_id, service_token=None, resource_namespace=None):
    if resource_namespace is None:
        resource_namespace = flask.current_app.config.get(
            "AUTH_SERVICE_NAMESPACE", "datastack"
        )
    service_token_local = (
        service_token
        if service_token
        else flask.current_app.config.get("AUTH_TOKEN")
    )
    try:
        table_mapping_token = (
            service_token_local
            if service_token_local
            else flask.g.auth_token
        )
        return dataset_from_table_id(
            resource_namespace, table_id, table_mapping_token
        )
    except RuntimeError:
        raise MACAuthorizationError(
            400,
            "invalid_table_id",
            msg="Invalid table_id for service",
            data={
                "table_id": table_id,
                "resource_namespace": resource_namespace,
            },
        )


def has_permission(auth_user, dataset, permission, ignore_tos=False):
    permissions_key = (
        PERMISSIONS_KEY_IGNORE_TOS
        if (ignore_tos and PERMISSIONS_KEY_IGNORE_TOS in auth_user)
        else PERMISSIONS_KEY
    )

    return permission in auth_user.get(permissions_key, {}).get(dataset, [])


def user_has_permission(
    permission, table_id, resource_namespace, service_token=None, ignore_tos=False
):
    if AUTH_DISABLED:
        return True

    token = (
        service_token
        if service_token
        else flask.current_app.config.get("AUTH_TOKEN", "")
    )

    dataset = dataset_from_table_id(resource_namespace, table_id, token)

    return has_permission(flask.g.auth_user, dataset, permission, ignore_tos)


def is_programmatic_access():
    auth_header = flask.request.headers.get("authorization")
    xrw_header = flask.request.headers.get("X-Requested-With")

    return xrw_header or auth_header or flask.request.environ.get("HTTP_ORIGIN")


def auth_required(
    func=None,
    *,
    required_permission=None,
    public_table_key=None,
    public_node_key=None,
    public_node_json_key=None,
    service_token=None,
):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if flask.request.method == "OPTIONS":
                return f(*args, **kwargs)

            debug_print(
                f"auth_required: required_permission:{required_permission} public_table_key:{public_table_key} public_node_key:{public_node_key} public_node_json_key:{public_node_json_key}"
            )

            if hasattr(flask.g, "auth_token"):
                # if authorization header has already been parsed, don't need to re-parse
                # this allows auth_required to be an optional decorator if auth_requires_role is also used
                return f(*args, **kwargs)

            flask.g.public_access_cache = None

            def lazy_check_public_access():
                debug_print(f"lazy_check_public_access {flask.g.public_access_cache}")
                if flask.g.public_access_cache is None:
                    if service_token and required_permission != "edit":
                        if public_node_key is not None:
                            flask.g.public_access_cache = is_root_public(
                                kwargs.get(public_table_key),
                                kwargs.get(public_node_key),
                                service_token,
                            )
                        elif public_node_json_key is not None:
                            debug_print(f"content-type:{flask.request.content_type}")
                            if flask.request.get_json(
                                force=True, silent=True
                            ) and isinstance(flask.request.json, dict):
                                node_ids = flask.request.json.get(public_node_json_key)
                                flask.g.public_access_cache = are_roots_public(
                                    kwargs.get(public_table_key),
                                    frozenset(node_ids),
                                    service_token,
                                )
                        elif public_table_key is not None:
                            flask.g.public_access_cache = table_has_public(
                                kwargs.get(public_table_key), service_token
                            )
                        else:
                            flask.g.public_access_cache = False
                    else:
                        flask.g.public_access_cache = False

                return flask.g.public_access_cache

            flask.g.public_access = lazy_check_public_access

            if AUTH_DISABLED:
                flask.g.auth_user = {
                    "id": 0,
                    "service_account": False,
                    "name": "AUTH_DISABLED",
                    "email": "AUTH_DISABLED@AUTH.DISABLED",
                    "admin": True,
                    "groups": [],
                    "permissions": {},
                }
                flask.g.auth_token = "AUTH_DISABLED"
                return f(*args, **kwargs)

            cookie_name = TOKEN_NAME
            token = flask.request.cookies.get(cookie_name)

            auth_header = flask.request.headers.get("authorization")

            programmatic_access = is_programmatic_access()

            AUTHORIZE_URI = "https://" + STICKY_AUTH_URL + "/api/v1/authorize"

            query_param_token = flask.request.args.get(TOKEN_NAME)

            if query_param_token:
                token = query_param_token

            auth_header = flask.request.headers.get("authorization")

            if auth_header:
                if not auth_header.startswith("Bearer "):
                    resp = MACAuthorizationError(
                        400,
                        "bad_auth_header",
                        "Authorization header must begin with 'Bearer'",
                    ).to_response()
                    resp.headers["WWW-Authenticate"] = (
                        'Bearer realm="'
                        + AUTHORIZE_URI
                        + '", error="invalid_request", error_description="Header must begin with \'Bearer\'"'
                    )
                    return resp
                else:  # auth header takes priority
                    token = auth_header.split(" ")[1]  # remove schema

            if programmatic_access:
                if not token and not flask.g.public_access():
                    resp = MACAuthorizationError(
                        401,
                        "no_token",
                        "Unauthorized - No Token Provided",
                    ).to_response()
                    resp.headers["WWW-Authenticate"] = (
                        'Bearer realm="' + AUTHORIZE_URI + '"'
                    )
                    return resp
            # direct browser access, or a non-browser request missing auth header (user error) TODO: check user agent to deliver 401 in this case
            else:
                if query_param_token:
                    resp = flask.make_response(
                        flask.redirect(
                            furl(flask.request.url).remove([TOKEN_NAME, "token"]).url,
                            code=302,
                        )
                    )
                    resp.set_cookie(
                        cookie_name, query_param_token, secure=True, httponly=True
                    )
                    return resp

            cached_user_data = get_user_cache(token) if token else None

            if cached_user_data:
                flask.g.auth_user = cached_user_data
                flask.g.auth_token = token
                return f(*args, **kwargs)
            elif not programmatic_access and not flask.g.public_access():
                return flask.redirect(
                    AUTHORIZE_URI + "?redirect=" + quote(flask.request.url), code=302
                )
            elif not flask.g.public_access():
                resp = MACAuthorizationError(
                    401, "invalid_token", "Unauthorized - Token is Invalid or Expired"
                ).to_response()
                resp.headers["WWW-Authenticate"] = (
                    'Bearer realm="'
                    + AUTHORIZE_URI
                    + '", error="invalid_token", error_description="Invalid/Expired Token"'
                )
                return resp
            else:
                flask.g.auth_user = {
                    "id": 0,
                    "service_account": False,
                    "name": "",
                    "email": "",
                    "admin": False,
                    "groups": [],
                    "permissions": {},
                }
                flask.g.auth_token = None
                return f(*args, **kwargs)

        return decorated_function

    if func:
        return decorator(func)
    else:
        return decorator


def auth_requires_admin(f):
    @wraps(f)
    @auth_required
    def decorated_function(*args, **kwargs):
        if flask.request.method == "OPTIONS":
            return f(*args, **kwargs)
        if AUTH_DISABLED:
            return f(*args, **kwargs)
        if not flask.g.auth_user["admin"]:
            resp = flask.Response("Requires superadmin privilege.", 403)
            return resp
        else:
            return f(*args, **kwargs)

    return decorated_function


def auth_requires_dataset_admin(
    service_token=None,
    dataset=None,
    table_arg="table_id",
    table_id=None,
    resource_namespace=None,
):
    def decorator(f):
        @wraps(f)
        @auth_required
        def decorated_function(*args, **kwargs):
            if flask.request.method == "OPTIONS":
                return f(*args, **kwargs)
            if AUTH_DISABLED:
                return f(*args, **kwargs)
            
            local_table_id = table_id
            if local_table_id is None:
                local_table_id = kwargs.get(table_arg)

            if local_table_id is None and dataset is None:
                return MACAuthorizationError(400, "missing_table_id", msg="Missing table_id").to_response()

            local_dataset = dataset
            if local_dataset is None:
                try:
                    local_dataset = dataset_from_table_id_from_request(local_table_id, service_token, resource_namespace)
                except MACAuthorizationError as e:
                    return e.to_response()
            if local_dataset in flask.g.auth_user["datasets_admin"]:
                return f(*args, **kwargs)
            else:
                required_role = "dataset_admin"
                message = "Missing role: {0} for dataset {1}".format(
                    required_role, local_dataset
                )
                return MACAuthorizationError(
                    403,
                    "missing_role",
                    msg=message,
                    data={
                        "required_role": required_role,
                        "auth_dataset": local_dataset,
                    },
                ).to_response()
        return decorated_function
    return decorator


def users_share_common_group(user_id, excluded_groups=None, service_token=None):
    excluded_groups = (
        excluded_groups
        if excluded_groups
        else flask.current_app.config.get("AUTH_SHARED_EXCLUDED_GROUPS", [])
    )

    if AUTH_DISABLED:
        return True

    target_user_data = user_id_to_user_cache_http(user_id, service_token)

    if target_user_data:
        request_user_groups = flask.g.auth_user["groups"]
        target_user_groups = target_user_data["groups"]

        shared_groups = [
            g
            for g in request_user_groups
            if g in target_user_groups and g not in excluded_groups
        ]

        if len(shared_groups) == 0:
            return False
        else:
            return True
    else:
        raise RuntimeError("user_data lookup request failed")


def auth_requires_permission(
    required_permission,
    public_table_key=None,
    public_node_key=None,
    public_node_json_key=None,
    service_token=None,
    dataset=None,
    table_arg="table_id",
    table_id=None,
    resource_namespace=None,
    ignore_tos=False,
):
    def decorator(f):
        @wraps(f)
        @auth_required(
            required_permission=required_permission,
            public_table_key=public_table_key,
            public_node_key=public_node_key,
            public_node_json_key=public_node_json_key,
            service_token=service_token,
        )
        def decorated_function(*args, **kwargs):
            if flask.request.method == "OPTIONS":
                return f(*args, **kwargs)
            if AUTH_DISABLED:
                return f(*args, **kwargs)
            local_table_id = table_id
            if local_table_id is None:
                local_table_id = kwargs.get(table_arg)

            if local_table_id is None and dataset is None:
                return MACAuthorizationError(400, "missing_table_id", msg="Missing table_id").to_response()

            local_dataset = dataset
            if local_dataset is None:
                try:
                    local_dataset = dataset_from_table_id_from_request(local_table_id, service_token, resource_namespace)
                except MACAuthorizationError as e:
                    return e.to_response()
            # public_access won't be true for edit requests
            if (
                has_permission(
                    flask.g.auth_user, local_dataset, required_permission, ignore_tos
                )
                or flask.g.public_access()
            ):
                return f(*args, **kwargs)
            else:
                if flask.g.auth_token:  # should always exist
                    try:
                        clear_user_cache_maybe(flask.g.auth_token)
                        # try again
                        cached_user_data = get_user_cache(flask.g.auth_token)
                        if cached_user_data:
                            flask.g.auth_user = cached_user_data
                            if has_permission(
                                flask.g.auth_user,
                                local_dataset,
                                required_permission,
                                ignore_tos,
                            ):
                                # cached permissions were out of date
                                return f(*args, **kwargs)
                    except RateLimitError:
                        pass

                missing_tos = flask.g.auth_user.get("missing_tos", [])
                relevant_tos = [
                    tos for tos in missing_tos if tos["dataset_name"] == local_dataset
                ]

                # only show missing terms of service if they would be granted permission by accepting it
                if len(relevant_tos) and (
                    PERMISSIONS_KEY_IGNORE_TOS
                    not in flask.g.auth_user  # backwards compatibility
                    or has_permission(
                        flask.g.auth_user,
                        local_dataset,
                        required_permission,
                        ignore_tos=True,
                    )
                ):
                    tos_form_url = f"https://{STICKY_AUTH_URL}/api/v1/tos/{relevant_tos[0]['tos_id']}/accept"

                    if is_programmatic_access():
                        return MACAuthorizationError(
                            403,
                            "missing_tos",
                            msg="Need to accept Terms of Service to access resource.",
                            data={
                                "tos_id": relevant_tos[0]["tos_id"],
                                "tos_name": relevant_tos[0]["tos_name"],
                                "tos_form_url": tos_form_url,
                            },
                        ).to_response()
                    else:
                        return flask.redirect(
                            tos_form_url + "?redirect=" + quote(flask.request.url),
                            code=302,
                        )
                message = "Missing permission: {0} for dataset {1}".format(
                    required_permission, local_dataset
                )
                resp = MACAuthorizationError(
                    403,
                    "missing_permission",
                    msg=message,
                    data={
                        "required_permission": required_permission,
                        "auth_dataset": local_dataset,
                    },
                ).to_response()

                return resp

        return decorated_function

    return decorator


def auth_requires_group(required_group):
    def decorator(f):
        @wraps(f)
        @auth_required
        def decorated_function(*args, **kwargs):
            if flask.request.method == "OPTIONS":
                return f(*args, **kwargs)

            if not AUTH_DISABLED and required_group not in flask.g.auth_user["groups"]:
                clear_user_cache_maybe(flask.g.auth_token)
                resp = flask.Response(
                    "Requires membership of group: {0}".format(required_group), 403
                )
                return resp

            return f(*args, **kwargs)

        return decorated_function

    return decorator
