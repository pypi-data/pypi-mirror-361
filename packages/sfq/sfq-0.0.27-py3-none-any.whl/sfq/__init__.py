"""
.. include:: ../../README.md
"""

import base64
import http.client
import json
import logging
import os
import time
import warnings
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Iterable, Literal, Optional, List, Tuple
from urllib.parse import quote, urlparse

__all__ = ["SFAuth"]  # https://pdoc.dev/docs/pdoc.html#control-what-is-documented

TRACE = 5
logging.addLevelName(TRACE, "TRACE")


def trace(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
    """Custom TRACE level logging function with redaction."""

    def _redact_sensitive(data: Any) -> Any:
        """Redacts sensitive keys from a dictionary or query string."""
        REDACT_VALUE = "*" * 8
        REDACT_KEYS = [
            "access_token",
            "authorization",
            "set-cookie",
            "cookie",
            "refresh_token",
            "client_secret",
        ]
        if isinstance(data, dict):
            return {
                k: (REDACT_VALUE if k.lower() in REDACT_KEYS else v)
                for k, v in data.items()
            }
        elif isinstance(data, (list, tuple)):
            return type(data)(
                (
                    (item[0], REDACT_VALUE)
                    if isinstance(item, tuple) and item[0].lower() in REDACT_KEYS
                    else item
                    for item in data
                )
            )
        elif isinstance(data, str):
            parts = data.split("&")
            for i, part in enumerate(parts):
                if "=" in part:
                    key, value = part.split("=", 1)
                    if key.lower() in REDACT_KEYS:
                        parts[i] = f"{key}={REDACT_VALUE}"
            return "&".join(parts)
        return data

    redacted_args = args
    if args:
        first = args[0]
        if isinstance(first, str):
            try:
                loaded = json.loads(first)
                first = loaded
            except (json.JSONDecodeError, TypeError):
                pass
        redacted_first = _redact_sensitive(first)
        redacted_args = (redacted_first,) + args[1:]

    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, redacted_args, **kwargs)


logging.Logger.trace = trace
logger = logging.getLogger("sfq")


class SFAuth:
    def __init__(
        self,
        instance_url: str,
        client_id: str,
        refresh_token: str,  # client_secret & refresh_token will swap positions 2025-AUG-1
        client_secret: str = "_deprecation_warning",  # mandatory after 2025-AUG-1
        api_version: str = "v64.0",
        token_endpoint: str = "/services/oauth2/token",
        access_token: Optional[str] = None,
        token_expiration_time: Optional[float] = None,
        token_lifetime: int = 15 * 60,
        user_agent: str = "sfq/0.0.27",
        sforce_client: str = "_auto",
        proxy: str = "_auto",
    ) -> None:
        """
        Initializes the SFAuth with necessary parameters.

        :param instance_url: The Salesforce instance URL.
        :param client_id: The client ID for OAuth.
        :param refresh_token: The refresh token for OAuth.
        :param client_secret: The client secret for OAuth.
        :param api_version: The Salesforce API version.
        :param token_endpoint: The token endpoint.
        :param access_token: The access token for the current session.
        :param token_expiration_time: The expiration time of the access token.
        :param token_lifetime: The lifetime of the access token in seconds.
        :param user_agent: Custom User-Agent string.
        :param sforce_client: Custom Application Identifier.
        :param proxy: The proxy configuration, "_auto" to use environment.
        """
        self.instance_url = self._format_instance_url(instance_url)
        """
        ### `instance_url`
        **The fully qualified Salesforce instance URL.**

        - Should end with `.my.salesforce.com`
        - No trailing slash

        **Examples:**
        - `https://sfq-dev-ed.trailblazer.my.salesforce.com`
        - `https://sfq.my.salesforce.com`
        - `https://sfq--dev.sandbox.my.salesforce.com`
        """

        self.client_id = client_id
        """
        ### `client_id`
        **The OAuth client ID.**

        - Uniquely identifies your **Connected App** in Salesforce
        - If using **Salesforce CLI**, this is `"PlatformCLI"`
        - For other apps, find this value in the **Connected App details**
        """

        self.client_secret = client_secret
        """
        ### `client_secret`
        **The OAuth client secret.**

        - Secret key associated with your Connected App
        - For **Salesforce CLI**, this is typically an empty string `""`
        - For custom apps, locate it in the **Connected App settings**
        """

        self.refresh_token = refresh_token
        """
        ### `refresh_token`
        **The OAuth refresh token.**

        - Used to fetch new access tokens when the current one expires
        - For CLI, obtain via:

          ```bash
          sf org display --json
        ````

        * For other apps, this value is returned during the **OAuth authorization flow**
            * 📖 [Salesforce OAuth Flows Documentation](https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_flows.htm&type=5)
        """

        self.api_version = api_version
        """

        ### `api_version`

        **The Salesforce API version to use.**

        * Must include the `"v"` prefix (e.g., `"v64.0"`)
        * Periodically updated to align with new Salesforce releases
        """

        self.token_endpoint = token_endpoint
        """

        ### `token_endpoint`

        **The token URL path for OAuth authentication.**

        * Defaults to Salesforce's `.well-known/openid-configuration` for *token* endpoint
        * Should start with a **leading slash**, e.g., `/services/oauth2/token`
        * No customization is typical, but internal designs may use custom ApexRest endpoints
          """

        self.access_token = access_token
        """

        ### `access_token`

        **The current OAuth access token.**

        * Used to authorize API requests
        * Does not include Bearer prefix, strictly the token
        """

        self.token_expiration_time = token_expiration_time
        """

        ### `token_expiration_time`

        **Unix timestamp (in seconds) for access token expiration.**

        * Managed automatically by the library
        * Useful for checking when to refresh the token
          """

        self.token_lifetime = token_lifetime
        """

        ### `token_lifetime`

        **Access token lifespan in seconds.**

        * Determined by your Connected App's session policies
        * Used to calculate when to refresh the token
          """

        self.user_agent = user_agent
        """

        ### `user_agent`

        **Custom User-Agent string for API calls.**

        * Included in HTTP request headers
        * Useful for identifying traffic in Salesforce `ApiEvent` logs
          """

        self.sforce_client = str(sforce_client).replace(",", "")
        """

        ### `sforce_client`

        **Custom application identifier.**

        * Included in the `Sforce-Call-Options` header
        * Useful for identifying traffic in Event Log Files
        * Commas are not allowed; will be stripped
        """

        self._auto_configure_proxy(proxy)
        self._high_api_usage_threshold = 80

        if sforce_client == "_auto":
            self.sforce_client = user_agent

        if self.client_secret == "_deprecation_warning":
            warnings.warn(
                "The 'client_secret' parameter will be mandatory and positional arguments will change after 1 August 2025. "
                "Please ensure explicit argument assignment and 'client_secret' inclusion when initializing the SFAuth object.",
                DeprecationWarning,
                stacklevel=2,
            )

            logger.debug(
                "Will be SFAuth(instance_url, client_id, client_secret, refresh_token) starting 1 August 2025... but please just use named arguments.."
            )

    def _format_instance_url(self, instance_url) -> str:
        """
        HTTPS is mandatory with Spring '21 release,
        This method ensures that the instance URL is formatted correctly.

        :param instance_url: The Salesforce instance URL.
        :return: The formatted instance URL.
        """
        if instance_url.startswith("https://"):
            return instance_url
        if instance_url.startswith("http://"):
            return instance_url.replace("http://", "https://")
        return f"https://{instance_url}"

    def _auto_configure_proxy(self, proxy: str) -> None:
        """
        Automatically configure the proxy based on the environment or provided value.
        """
        if proxy == "_auto":
            self.proxy = os.environ.get("https_proxy")  # HTTPs is mandatory
            if self.proxy:
                logger.debug("Auto-configured proxy: %s", self.proxy)
        else:
            self.proxy = proxy
            logger.debug("Using configured proxy: %s", self.proxy)

    def _prepare_payload(self) -> Dict[str, Optional[str]]:
        """
        Prepare the payload for the token request.

        This method constructs a dictionary containing the necessary parameters
        for a token request using the refresh token grant type. It includes
        the client ID, client secret, and refresh token if they are available.

        Returns:
            Dict[str, Optional[str]]: A dictionary containing the payload for the token request.
        """
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        if self.client_secret == "_deprecation_warning":
            logger.warning(
                "The SFQ library is making a breaking change (2025-AUG-1) to require the 'client_secret' parameter to be assigned when initializing the SFAuth object. "
                "In addition, positional arguments will change. Please ensure explicit argument assignment and 'client_secret' inclusion when initializing the SFAuth object to avoid impact."
            )
            payload.pop("client_secret")

        if not self.client_secret:
            payload.pop("client_secret")

        return payload

    def _create_connection(self, netloc: str) -> http.client.HTTPConnection:
        """
        Create a connection using HTTP or HTTPS, with optional proxy support.

        :param netloc: The target host and port from the parsed instance URL.
        :return: An HTTP(S)Connection object.
        """
        if self.proxy:
            proxy_url = urlparse(self.proxy)
            logger.trace("Using proxy: %s", self.proxy)
            conn = http.client.HTTPSConnection(proxy_url.hostname, proxy_url.port)
            conn.set_tunnel(netloc)
            logger.trace("Using proxy tunnel to %s", netloc)
        else:
            conn = http.client.HTTPSConnection(netloc)
            logger.trace("Direct connection to %s", netloc)
        return conn

    def _send_request(
        self,
        method: str,
        endpoint: str,
        headers: Dict[str, str],
        body: Optional[str] = None,
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        Unified request method with built-in logging and error handling.

        :param method: HTTP method to use.
        :param endpoint: Target API endpoint.
        :param headers: HTTP headers.
        :param body: Optional request body.
        :param timeout: Optional timeout in seconds.
        :return: Tuple of HTTP status code and response body as a string.
        """
        parsed_url = urlparse(self.instance_url)
        conn = self._create_connection(parsed_url.netloc)

        try:
            logger.trace("Request method: %s", method)
            logger.trace("Request endpoint: %s", endpoint)
            logger.trace("Request headers: %s", headers)
            if body:
                logger.trace("Request body: %s", body)

            conn.request(method, endpoint, body=body, headers=headers)
            response = conn.getresponse()
            self._http_resp_header_logic(response)

            data = response.read().decode("utf-8")
            logger.trace("Response status: %s", response.status)
            logger.trace("Response body: %s", data)
            return response.status, data

        except Exception as err:
            logger.exception("HTTP request failed: %s", err)
            return None, None

        finally:
            logger.trace("Closing connection...")
            conn.close()

    def _new_token_request(self, payload: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Perform a new token request using the provided payload.

        :param payload: Payload for the token request.
        :return: Parsed JSON response or None on failure.
        """
        headers = self._get_common_headers(recursive_call=True)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        del headers["Authorization"]

        body = "&".join(f"{key}={quote(str(value))}" for key, value in payload.items())
        status, data = self._send_request("POST", self.token_endpoint, headers, body)

        if status == 200:
            logger.trace("Token refresh successful.")
            return json.loads(data)

        if status:
            logger.error("Token refresh failed: %s", status)
            logger.debug("Response body: %s", data)

        return None

    def _http_resp_header_logic(self, response: http.client.HTTPResponse) -> None:
        """
        Perform additional logic based on the HTTP response headers.

        :param response: The HTTP response object.
        :return: None
        """
        logger.trace(
            "Response status: %s, reason: %s", response.status, response.reason
        )
        headers = response.getheaders()
        headers_list = [(k, v) for k, v in headers if not v.startswith("BrowserId=")]
        logger.trace("Response headers: %s", headers_list)
        for key, value in headers_list:
            if key == "Sforce-Limit-Info":
                current_api_calls = int(value.split("=")[1].split("/")[0])
                maximum_api_calls = int(value.split("=")[1].split("/")[1])
                usage_percentage = round(current_api_calls / maximum_api_calls * 100, 2)
                if usage_percentage > self._high_api_usage_threshold:
                    logger.warning(
                        "High API usage: %s/%s (%s%%)",
                        current_api_calls,
                        maximum_api_calls,
                        usage_percentage,
                    )
                else:
                    logger.debug(
                        "API usage: %s/%s (%s%%)",
                        current_api_calls,
                        maximum_api_calls,
                        usage_percentage,
                    )

    def _refresh_token_if_needed(self) -> Optional[str]:
        """
        Automatically refresh the access token if it has expired or is missing.

        :return: A valid access token or None if refresh failed.
        """
        if self.access_token and not self._is_token_expired():
            return self.access_token

        logger.trace("Access token expired or missing, refreshing...")
        payload = self._prepare_payload()
        token_data = self._new_token_request(payload)

        if token_data:
            self.access_token = token_data.get("access_token")
            issued_at = token_data.get("issued_at")

            try:
                self.org_id = token_data.get("id").split("/")[4]
                self.user_id = token_data.get("id").split("/")[5]
                logger.trace(
                    "Authenticated as user %s for org %s (%s)",
                    self.user_id,
                    self.org_id,
                    token_data.get("instance_url"),
                )
            except (IndexError, KeyError):
                logger.error("Failed to extract org/user IDs from token response.")

            if self.access_token and issued_at:
                self.token_expiration_time = int(issued_at) + self.token_lifetime
                logger.trace("New token expires at %s", self.token_expiration_time)
                return self.access_token

        logger.error("Failed to obtain access token.")
        return None

    def _get_common_headers(self, recursive_call: bool = False) -> Dict[str, str]:
        """
        Generate common headers for API requests.

        :return: A dictionary of common headers.
        """
        if not recursive_call:
            self._refresh_token_if_needed()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent,
            "Sforce-Call-Options": f"client={self.sforce_client}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _is_token_expired(self) -> bool:
        """
        Check if the access token has expired.

        :return: True if token is expired or missing, False otherwise.
        """
        try:
            return time.time() >= float(self.token_expiration_time)
        except (TypeError, ValueError):
            logger.warning("Token expiration check failed. Treating token as expired.")
            return True

    def read_static_resource_name(
        self, resource_name: str, namespace: Optional[str] = None
    ) -> Optional[str]:
        """
        Read a static resource for a given name from the Salesforce instance.

        :param resource_name: Name of the static resource to read.
        :param namespace: Namespace of the static resource to read (default is None).
        :return: Static resource content or None on failure.
        """
        _safe_resource_name = quote(resource_name, safe="")
        query = f"SELECT Id FROM StaticResource WHERE Name = '{_safe_resource_name}'"
        if namespace:
            namespace = quote(namespace, safe="")
            query += f" AND NamespacePrefix = '{namespace}'"
        query += " LIMIT 1"
        _static_resource_id_response = self.query(query)

        if (
            _static_resource_id_response
            and _static_resource_id_response.get("records")
            and len(_static_resource_id_response["records"]) > 0
        ):
            return self.read_static_resource_id(
                _static_resource_id_response["records"][0].get("Id")
            )

        logger.error(f"Failed to read static resource with name {_safe_resource_name}.")
        return None

    def read_static_resource_id(self, resource_id: str) -> Optional[str]:
        """
        Read a static resource for a given ID from the Salesforce instance.

        :param resource_id: ID of the static resource to read.
        :return: Static resource content or None on failure.
        """
        endpoint = f"/services/data/{self.api_version}/sobjects/StaticResource/{resource_id}/Body"
        headers = self._get_common_headers()
        status, data = self._send_request("GET", endpoint, headers)

        if status == 200:
            logger.debug("Static resource fetched successfully.")
            return data

        logger.error("Failed to fetch static resource: %s", status)
        return None

    def update_static_resource_name(
        self, resource_name: str, data: str, namespace: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a static resource for a given name in the Salesforce instance.

        :param resource_name: Name of the static resource to update.
        :param data: Content to update the static resource with.
        :param namespace: Optional namespace to search for the static resource.
        :return: Static resource content or None on failure.
        """
        safe_resource_name = quote(resource_name, safe="")
        query = f"SELECT Id FROM StaticResource WHERE Name = '{safe_resource_name}'"
        if namespace:
            namespace = quote(namespace, safe="")
            query += f" AND NamespacePrefix = '{namespace}'"
        query += " LIMIT 1"

        static_resource_id_response = self.query(query)

        if (
            static_resource_id_response
            and static_resource_id_response.get("records")
            and len(static_resource_id_response["records"]) > 0
        ):
            return self.update_static_resource_id(
                static_resource_id_response["records"][0].get("Id"), data
            )

        logger.error(
            f"Failed to update static resource with name {safe_resource_name}."
        )
        return None

    def update_static_resource_id(
        self, resource_id: str, data: str
    ) -> Optional[Dict[str, Any]]:
        """
        Replace the content of a static resource in the Salesforce instance by ID.

        :param resource_id: ID of the static resource to update.
        :param data: Content to update the static resource with.
        :return: Parsed JSON response or None on failure.
        """
        payload = {"Body": base64.b64encode(data.encode("utf-8")).decode("utf-8")}

        endpoint = (
            f"/services/data/{self.api_version}/sobjects/StaticResource/{resource_id}"
        )
        headers = self._get_common_headers()

        status_code, response_data = self._send_request(
            method="PATCH",
            endpoint=endpoint,
            headers=headers,
            body=json.dumps(payload),
        )

        if status_code == 200:
            logger.debug("Patch Static Resource request successful.")
            return json.loads(response_data)

        logger.error(
            "Patch Static Resource API request failed: %s",
            status_code,
        )
        logger.debug("Response body: %s", response_data)

        return None

    def limits(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the current limits for the Salesforce instance.

        :return: Parsed JSON response or None on failure.
        """
        endpoint = f"/services/data/{self.api_version}/limits"
        headers = self._get_common_headers()

        status, data = self._send_request("GET", endpoint, headers)

        if status == 200:
            logger.debug("Limits fetched successfully.")
            return json.loads(data)

        logger.error("Failed to fetch limits: %s", status)
        return None

    def _paginate_query_result(self, initial_result: dict, headers: dict) -> dict:
        """
        Helper to paginate Salesforce query results (for both query and cquery).
        Returns a dict with all records combined.
        """
        records = list(initial_result.get("records", []))
        done = initial_result.get("done", True)
        next_url = initial_result.get("nextRecordsUrl")
        total_size = initial_result.get("totalSize", len(records))

        while not done and next_url:
            status_code, data = self._send_request(
                method="GET",
                endpoint=next_url,
                headers=headers,
            )
            if status_code == 200:
                next_result = json.loads(data)
                records.extend(next_result.get("records", []))
                done = next_result.get("done", True)
                next_url = next_result.get("nextRecordsUrl")
                total_size = next_result.get("totalSize", total_size)
            else:
                logger.error("Failed to fetch next records: %s", data)
                break

        paginated = dict(initial_result)
        paginated["records"] = records
        paginated["done"] = done
        paginated["totalSize"] = total_size
        if "nextRecordsUrl" in paginated:
            del paginated["nextRecordsUrl"]
        return paginated

    def query(self, query: str, tooling: bool = False) -> Optional[Dict[str, Any]]:
        """
        Execute a SOQL query using the REST or Tooling API.

        :param query: The SOQL query string.
        :param tooling: If True, use the Tooling API endpoint.
        :return: Parsed JSON response or None on failure.
        """
        endpoint = f"/services/data/{self.api_version}/"
        endpoint += "tooling/query" if tooling else "query"
        query_string = f"?q={quote(query)}"
        endpoint += query_string
        headers = self._get_common_headers()

        try:
            status_code, data = self._send_request(
                method="GET",
                endpoint=endpoint,
                headers=headers,
            )
            if status_code == 200:
                result = json.loads(data)
                paginated = self._paginate_query_result(result, headers)
                logger.debug(
                    "Query successful, returned %s records: %r",
                    paginated.get("totalSize"),
                    query,
                )
                logger.trace("Query full response: %s", paginated)
                return paginated
            else:
                logger.debug("Query failed: %r", query)
                logger.error(
                    "Query failed with HTTP status %s",
                    status_code,
                )
                logger.debug("Query response: %s", data)
        except Exception as err:
            logger.exception("Exception during query: %s", err)

        return None

    def tooling_query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Execute a SOQL query using the Tooling API.

        :param query: The SOQL query string.
        :return: Parsed JSON response or None on failure.
        """
        return self.query(query, tooling=True)

    def get_sobject_prefixes(
        self, key_type: Literal["id", "name"] = "id"
    ) -> Optional[Dict[str, str]]:
        """
        Fetch all key prefixes from the Salesforce instance and map them to sObject names or vice versa.

        :param key_type: The type of key to return. Either 'id' (prefix) or 'name' (sObject).
        :return: A dictionary mapping key prefixes to sObject names or None on failure.
        """
        valid_key_types = {"id", "name"}
        if key_type not in valid_key_types:
            logger.error(
                "Invalid key type: %s, must be one of: %s",
                key_type,
                ", ".join(valid_key_types),
            )
            return None

        endpoint = f"/services/data/{self.api_version}/sobjects/"
        headers = self._get_common_headers()

        prefixes = {}

        try:
            logger.trace("Request endpoint: %s", endpoint)
            logger.trace("Request headers: %s", headers)

            status_code, data = self._send_request(
                method="GET",
                endpoint=endpoint,
                headers=headers,
            )

            if status_code == 200:
                logger.debug("Key prefixes API request successful.")
                logger.trace("Response body: %s", data)
                for sobject in json.loads(data)["sobjects"]:
                    key_prefix = sobject.get("keyPrefix")
                    name = sobject.get("name")
                    if not key_prefix or not name:
                        continue

                    if key_type == "id":
                        prefixes[key_prefix] = name
                    elif key_type == "name":
                        prefixes[name] = key_prefix

                logger.debug("Key prefixes: %s", prefixes)
                return prefixes

            logger.error(
                "Key prefixes API request failed: %s",
                status_code,
            )
            logger.debug("Response body: %s", data)

        except Exception as err:
            logger.exception("Exception during key prefixes API request: %s", err)

        return None

    def cquery(
        self, query_dict: dict[str, str], batch_size: int = 25, max_workers: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute multiple SOQL queries using the Composite Batch API with threading to reduce network overhead.
        The function returns a dictionary mapping the original keys to their corresponding batch response.
        The function requires a dictionary of SOQL queries with keys as logical names (referenceId) and values as SOQL queries.
        Each query (subrequest) is counted as a unique API request against Salesforce governance limits.

        :param query_dict: A dictionary of SOQL queries with keys as logical names and values as SOQL queries.
        :param batch_size: The number of queries to include in each batch (default is 25).
        :param max_workers: The maximum number of threads to spawn for concurrent execution (default is None).
        :return: Dict mapping the original keys to their corresponding batch response or None on failure.
        """
        if not query_dict:
            logger.warning("No queries to execute.")
            return None

        def _execute_batch(batch_keys, batch_queries):
            endpoint = f"/services/data/{self.api_version}/composite/batch"
            headers = self._get_common_headers()

            payload = {
                "haltOnError": False,
                "batchRequests": [
                    {
                        "method": "GET",
                        "url": f"/services/data/{self.api_version}/query?q={quote(query)}",
                    }
                    for query in batch_queries
                ],
            }

            status_code, data = self._send_request(
                method="POST",
                endpoint=endpoint,
                headers=headers,
                body=json.dumps(payload),
            )

            batch_results = {}
            if status_code == 200:
                logger.debug("Composite query successful.")
                logger.trace("Composite query full response: %s", data)
                results = json.loads(data).get("results", [])
                for i, result in enumerate(results):
                    key = batch_keys[i]
                    if result.get("statusCode") == 200 and "result" in result:
                        paginated = self._paginate_query_result(result["result"], headers)
                        batch_results[key] = paginated
                    else:
                        logger.error("Query failed for key %s: %s", key, result)
                        batch_results[key] = result
            else:
                logger.error(
                    "Composite query failed with HTTP status %s (%s)",
                    status_code,
                    data,
                )
                for i, key in enumerate(batch_keys):
                    batch_results[key] = data
                logger.trace("Composite query response: %s", data)

            return batch_results

        keys = list(query_dict.keys())
        results_dict = OrderedDict()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            BATCH_SIZE = batch_size
            for i in range(0, len(keys), BATCH_SIZE):
                batch_keys = keys[i : i + BATCH_SIZE]
                batch_queries = [query_dict[key] for key in batch_keys]
                futures.append(executor.submit(_execute_batch, batch_keys, batch_queries))

            for future in as_completed(futures):
                results_dict.update(future.result())

        logger.trace("Composite query results: %s", results_dict)
        return results_dict

    def cdelete(
        self, ids: Iterable[str], batch_size: int = 200, max_workers: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute the Collections Delete API to delete multiple records using multithreading.

        :param ids: A list of record IDs to delete.
        :param batch_size: The number of records to delete in each batch (default is 200).
        :param max_workers: The maximum number of threads to spawn for concurrent execution (default is None).
        :return: Combined JSON response from all batches or None on complete failure.
        """
        ids = list(ids)
        chunks = [ids[i : i + batch_size] for i in range(0, len(ids), batch_size)]

        def delete_chunk(chunk: List[str]) -> Optional[Dict[str, Any]]:
            endpoint = f"/services/data/{self.api_version}/composite/sobjects?ids={','.join(chunk)}&allOrNone=false"
            headers = self._get_common_headers()

            status_code, resp_data = self._send_request(
                method="DELETE",
                endpoint=endpoint,
                headers=headers,
            )

            if status_code == 200:
                logger.debug("Collections delete API response without errors.")
                return json.loads(resp_data)
            else:
                logger.error("Collections delete API request failed: %s", status_code)
                logger.debug("Response body: %s", resp_data)
                return None

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(delete_chunk, chunk) for chunk in chunks]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        combined_response = [
            item
            for result in results
            for item in (result if isinstance(result, list) else [result])
            if isinstance(result, (dict, list))
        ]
        return combined_response or None

    def _cupdate(self, update_dict: Dict[str, Any], batch_size: int = 25, max_workers: int = None) -> Optional[Dict[str, Any]]:
        """
        Execute the Composite Update API to update multiple records.

        :param update_dict: A dictionary of keys of records to be updated, and a dictionary of field-value pairs to be updated, with a special key '_' overriding the sObject type which is otherwise inferred from the key. Example:
            {'001aj00000C8kJhAAJ': {'Subject': 'Easily updated via SFQ'}, '00aaj000006wtdcAAA': {'_': 'CaseComment', 'IsPublished': False}, '001aj0000002yJRCAY': {'_': 'IdeaComment', 'CommentBody': 'Hello World!'}} 
        :param batch_size: The number of records to update in each batch (default is 25).
        :return: JSON response from the update request or None on failure.
        """
        allOrNone = False
        endpoint = f"/services/data/{self.api_version}/composite"

        compositeRequest_payload = []
        sobject_prefixes = {}

        for key, record in update_dict.items():
            sobject = record.copy().pop("_", None)
            if not sobject and not sobject_prefixes:
                sobject_prefixes = self.get_sobject_prefixes()
            
            if not sobject:
                sobject = str(sobject_prefixes.get(str(key[:3]), None))
            
            compositeRequest_payload.append(
                {
                    'method': 'PATCH',
                    'url': f"/services/data/{self.api_version}/sobjects/{sobject}/{key}",
                    'referenceId': key,
                    'body': record,
                }
            )

        chunks = [compositeRequest_payload[i:i+batch_size] for i in range(0, len(compositeRequest_payload), batch_size)]

        def update_chunk(chunk: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
            payload = {
                "allOrNone": bool(allOrNone),
                "compositeRequest": chunk
            }

            status_code, resp_data = self._send_request(
                method="POST",
                endpoint=endpoint,
                headers=self._get_common_headers(),
                body=json.dumps(payload),
            )

            if status_code == 200:
                logger.debug("Composite update API response without errors.")
                return json.loads(resp_data)
            else:
                logger.error("Composite update API request failed: %s", status_code)
                logger.debug("Response body: %s", resp_data)
                return None

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(update_chunk, chunk) for chunk in chunks]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        combined_response = [
            item
            for result in results
            for item in (result if isinstance(result, list) else [result])
            if isinstance(result, (dict, list))
        ]
        
        return combined_response or None
