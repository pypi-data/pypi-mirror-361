import httpx
import sys
import datetime
from logging import getLogger
from patroni_monitoring.constants import Status, LEADERS
from urllib import parse as urlparse

class PatroniAPI:
    """A class to interact with the Patroni API for cluster monitoring."""
    def __init__(self, url: str, timeout: int) -> None:
        self._logger = getLogger(__name__)
        self.base_url = url
        self.__scheme = urlparse.urlparse(url).scheme
        if self.__scheme not in ["http", "https"]:
            self._logger.error("Invalid URL scheme: %s. Expected 'http' or 'https'.", self.__scheme)
            sys.exit(Status.UNKNOWN.value)
        self.__port = urlparse.urlparse(url).port
        if self.__port is None:
            self._logger.error("Port is not specified in the URL: %s", url)
            sys.exit(Status.UNKNOWN.value)
        self._logger.debug("Scheme: %s, port: %s", self.__scheme, self.__port)
        self._scope = None
        self._cluster_info = None
        self._members = []
        self._current_time = None
        self._timeout = timeout

    def _get_cluster_info(self) -> dict:
        """
        Fetches cluster information from the Patroni API.
        Returns:
            dict: A dictionary containing cluster information.
        """
        with httpx.Client() as client:
            try:
                response = client.get(f"{self.base_url}/cluster", timeout=self._timeout)
            except httpx.ConnectError as connect_error:
                self._logger.error("Failed to connect to Patroni API at %s: %s", self.base_url, connect_error)
                sys.exit(Status.UNKNOWN.value)
            except httpx.ConnectTimeout:
                self._logger.error("Connection to Patroni API at %s time out after %s seconds", self.base_url, self._timeout)
                sys.exit(Status.UNKNOWN.value)
            except KeyboardInterrupt:
                self._logger.error("Keyboard interrupt received, exiting...")
                sys.exit(Status.UNKNOWN.value)
            return response.json()

    @property
    def scope(self) -> str:
        """
        Returns the scope of the cluster.
        If the scope is not set, it fetches the cluster information to determine the scope.
        Returns:
            str: The scope of the cluster.
        """
        if self._scope is None:
            cluster_info = self._get_cluster_info()
            self._scope = cluster_info.get("scope", "unknown")
        return self._scope

    @property
    def cluster_info(self) -> dict:
        """
        Returns the cluster information.
        If the cluster information is not set, it fetches it from the Patroni API.
        Returns:
            dict: A dictionary containing cluster information.
        """
        if self._cluster_info is None:
            self._cluster_info = self._get_cluster_info()
        return self._cluster_info

    @property
    def members(self) -> list:
        """
        Returns the list of members in the cluster.
        If the members are not set, it fetches them from the cluster information.
        Returns:
            list: A list of dictionaries containing member information.
        """
        if not self._members:
            cluster_info = self.cluster_info
            self._members = cluster_info.get("members", [])
        return self._members

    def _get_member_by_api_uri(self, api_uri: str) -> dict:
        """
        Returns a member's information by its name.
        Args:
            name (str): The name of the member.
        Returns:
            dict: A dictionary containing the member's information.
        """
        with httpx.Client() as client:
            try:
                response = client.get(api_uri, timeout=self._timeout)
            except httpx.ConnectError as connect_error:
                self._logger.error("Failed to connect to Patroni API at %s: %s", self.base_url, connect_error)
                sys.exit(Status.UNKNOWN.value)
            except httpx.ConnectTimeout:
                self._logger.error("Connection to Patroni API at %s time out after %s seconds", self.base_url, self._timeout)
                sys.exit(Status.UNKNOWN.value)
            except KeyboardInterrupt:
                self._logger.error("Keyboard interrupt received, exiting...")
                sys.exit(Status.UNKNOWN.value)
            return response.json()

    def __liveness(self, api_uri: str) -> bool:
        """
        Checks the liveness of the Patroni API.
        Returns:
            bool: True if the API is alive, False otherwise.
        """
        with httpx.Client() as client:
            try:
                response = client.get(api_uri, timeout=self._timeout)
                self._logger.debug("uri: %s code: %s", api_uri, response.status_code)
                return response.status_code == 200
            except httpx.ConnectError as connect_error:
                self._logger.error("Failed to connect to Patroni API at %s: %s", self.base_url, connect_error)
                sys.exit(Status.UNKNOWN.value)
            except httpx.ConnectTimeout:
                self._logger.error("Connection to Patroni API at %s timed out after %s seconds", self.base_url, self._timeout)
                sys.exit(Status.UNKNOWN.value)
            except KeyboardInterrupt:
                self._logger.error("Keyboard interrupt received, exiting...")
                sys.exit(Status.UNKNOWN.value)

    def __sync_mode(self, host) -> str:
        """
        Determines the sync mode of the cluster.
        Returns:
            str: The sync mode of the cluster.
        """
        sync_mode = "unknown"
        with httpx.Client() as client:
            try:
                response = client.get(f"{host}/sync", timeout=self._timeout)
                if response.status_code == 200:
                    sync_mode = "sync"
                    self._logger.debug("Sync mode: %s", sync_mode)
                    return sync_mode
                response = client.get(f"{host}/async", timeout=self._timeout)
                if response.status_code == 200:
                    sync_mode = "async"
                    self._logger.debug("Sync mode: %s", sync_mode)
                    return sync_mode
                self._logger.error("Failed to determine sync mode for host %s", host)
                sys.exit(Status.UNKNOWN.value)
            except httpx.ConnectError as connect_error:
                self._logger.error("Failed to connect to Patroni API at %s: %s", self.base_url, connect_error)
                sys.exit(Status.UNKNOWN.value)
            except httpx.ConnectTimeout:
                self._logger.error("Connection to Patroni API at %s timed out after %s seconds", self.base_url, self._timeout)
                sys.exit(Status.UNKNOWN.value)
            except KeyboardInterrupt:
                self._logger.error("Keyboard interrupt received, exiting...")
                sys.exit(Status.UNKNOWN.value)
        return sync_mode

    def __replication_lag(self, uri:str , lag: int) -> bool:
        """
        Calculates the replication lag for a member.
        Args:
            member (dict): A dictionary containing member information.
        Returns:
            int: The replication lag in bytes.
        """
        with httpx.Client() as client:
            try:
                request_uri = f"{uri}?lag={lag}"
                response = client.get(request_uri, timeout=self._timeout)
                self._logger.debug("uri: %s code: %s", request_uri, response.status_code)
                return not response.status_code == 200
            except httpx.ConnectError as connect_error:
                self._logger.error("Failed to connect to Patroni API at %s: %s", self.base_url, connect_error)
                sys.exit(Status.UNKNOWN.value)
            except httpx.ConnectTimeout:
                self._logger.error("Connection to Patroni API at %s timed out after %s seconds", self.base_url, self._timeout)
                sys.exit(Status.UNKNOWN.value)
            except KeyboardInterrupt:
                self._logger.error("Keyboard interrupt received, exiting...")
                sys.exit(Status.UNKNOWN.value)

    def cluster_status(self, lag: dict) -> list:
        """
        Returns the status of the cluster.
        If the cluster information is not set, it fetches it from the Patroni API.
        Args:
            lag (dict): A dictionary containing the warning and critical replication lag thresholds in bytes.
                        Example: {'warning': 1000000, 'critical': 2000000}
        Returns:
            str: The status of the cluster.
        """
        results = []
        for member in self.members:
            member_result = {}
            lag_status = "N/A"
            sync_mode = "N/A"
            member_role = member.get("role")
            self._current_time = datetime.datetime.now(datetime.timezone.utc).astimezone()
            host_api = f"{self.__scheme}://{member.get('host')}:{self.__port}"
            member_health = self._get_member_by_api_uri(f"{host_api}/patroni")
            xlog_data = member_health.get("xlog")
            if member_role not in LEADERS:
                lag_status = Status.OK.name
                sync_mode = self.__sync_mode(host=host_api)
                request_uri = urlparse.urljoin(host_api, "/replica")
                lag_check = self.__replication_lag(uri=request_uri, lag=lag.get("critical", 0))
                if lag_check:
                    lag_status = Status.CRITICAL.name
                else:
                    lag_check = self.__replication_lag(uri=request_uri, lag=lag.get("warning", 0))
                    if lag_check:
                        lag_status = Status.WARNING.name
                self._logger.debug("Member: %s, Role: %s, Sync Mode: %s, Lag Status: %s",
                               member.get("name"), member_role, sync_mode, lag_status)
            member_result.update({
                "name": member.get("name"),
                "role": member_role,
                "running": self.__liveness(api_uri=f"{self.__scheme}://{member.get('host')}:{self.__port}/liveness"),
                "sync_mode": sync_mode,
                "replica_lag": lag_status,
                "Start_time": member_health.get("postmaster_start_time"),
                "timeline": member_health.get("timeline"),
                "version": member_health.get("server_version"),
                "pending_restart": member_health.get("pending_restart", False),
                "xlog_paused": xlog_data.get("paused", "N/A") if xlog_data is not None else "N/A",
            })
            results.append(member_result)
        return results