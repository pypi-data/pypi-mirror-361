import logging
import sys
from patroni_monitoring.constants import Status, LEADERS

class Monitoring:
    def __init__(self,
            results: list,
            status: Status = Status.UNKNOWN) -> None:
        self._status = status
        self._message = []
        self._logger = logging.getLogger(__name__)
        self._results = results
        self._leader_results = self.__filter_leader(results)

    def __check_xlog_paused(self, xlog_paused: bool) -> None:
        """
        Checks if the xlog is paused.
        Args:
            xlog_paused (bool): Indicates if the xlog is paused.
        """
        self._logger.debug("Checking if xlog is paused: %s", xlog_paused)
        if xlog_paused:
            status = Status.CRITICAL
        else:
            status = Status.OK
        if status.value > self._status.value:
            self._status = status
            self._message.append("XLOG is paused")

    def __check_pending_restart(self, pending_restart: bool) -> None:
        """
        Checks if the member is pending restart.
        Args:
            pending_restart (bool): Indicates if the member is pending restart.
        """
        if pending_restart:
            status = Status.WARNING
            self._message.append("Member is pending restart")
        else:
            status = Status.OK
        if status.value > self._status.value:
            self._status = status

    def __filter_leader(self, results: list) -> dict:
        """
        Filters out the leader from the results.
        """
        for result in results:
            if result.get("role") in LEADERS:
                self._logger.debug("Found leader: %s", result.get("name"))
                return result
        self._logger.critical("No leader found in the results")
        sys.exit(Status.UNKNOWN.value)

    def __check_running(self, result) -> None:
        """
        Check if all members are running.
        """
        self._logger.debug("Checking if all members are running")
        status = Status.OK
        if not result.get("running"):
            self._logger.debug("Member %s is not running", result.get("name"))
            self._message.append(f"Member {result.get('name')} is not running")
            status = Status.CRITICAL
        if status.value > self._status.value:
            self._status = status

    def __check_lag(self, lag_status: str) -> None:
        """
        Check the replication lag status.
        Args:
            lag_status (str): The replication lag status.
        """
        status = Status.UNKNOWN
        if lag_status == Status.CRITICAL.name:
            self._message.append("Replication lag is critical")
            status = Status.CRITICAL
        elif lag_status == Status.WARNING.name:
            self._message.append("Replication lag is warning")
        elif lag_status == Status.OK.name:
            self._logger.debug("Replication lag is OK")
            status = Status.OK
        self._logger.debug("Replication lag status: %s", status.name)
        if status.value > self._status.value:
            self._status = status

    def _check_results(self) -> None:
        """
        """
        self._status = Status.OK
        for result in self._results:
            if result.get("role") == "leader":
                continue
            if result.get("role") == "standby_leader":
                continue
            self.__check_pending_restart(result.get("pending_restart"))
            self.__check_xlog_paused(result.get("xlog_paused"))
            self.__check_running(result)
            self.__check_lag(result.get("replica_lag", "N/A"))


    @property
    def status(self) -> int:
        """
        Returns the status of the monitoring.
        Returns:
            int: The status code (0 for OK, 1 for WARNING, 2 for CRITICAL, 3 for UNKNOWN).
        """
        self._check_results()
        message = self._message if self._message else ["No issues were found"]
        self._logger.warning("Issues: %s", ", ".join(message))
        self._logger.info("Status: %s", self._status.name)
        return self._status.value