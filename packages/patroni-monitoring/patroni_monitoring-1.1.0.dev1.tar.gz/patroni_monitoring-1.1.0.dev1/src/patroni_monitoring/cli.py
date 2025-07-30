import logging
import tabulate
import sys
from patroni_monitoring.patroni import PatroniAPI
from patroni_monitoring.monitoring import Monitoring
from patroni_monitoring.arguments import arguments
from patroni_monitoring.constants import Status

def cli():
    _logger = logging.getLogger("patroni_monitoring")
    _logger.addHandler(logging.StreamHandler())
    args = arguments()
    _logger.setLevel(args.log_level.upper())
    if args.warning < 0:
        _logger.error("Warning threshold must be a non-negative integer")
        _logger.error("Warning: %s", args.warning)
        _logger.error("Critical: %s", args.critical)
        sys.exit(Status.UNKNOWN.value)
    if args.critical < 0:
        _logger.error("Critical threshold must be a non-negative integer")
        _logger.error("Warning: %s", args.warning)
        _logger.error("Critical: %s", args.critical)
        sys.exit(Status.UNKNOWN.value)
    if args.delay_warning < 0:
        _logger.error("Warning delay threshold must be a non-negative float")
        _logger.error("Warning delay: %s", args.delay_warning)
        _logger.error("Critical delay: %s", args.delay_critical)
        sys.exit(Status.UNKNOWN.value)
    if args.delay_critical < 0:
        _logger.error("Critical delay threshold must be a non-negative float")
        _logger.error("Warning delay: %s", args.delay_warning)
        _logger.error("Critical delay: %s", args.delay_critical)
        sys.exit(Status.UNKNOWN.value)
    if args.warning > args.critical:
        _logger.error("Warning threshold must be less than critical threshold")
        _logger.error("Warning: %s", args.warning)
        _logger.error("Critical: %s", args.critical)
        sys.exit(Status.UNKNOWN.value)
    if args.delay_warning > args.delay_critical:
        _logger.error("Delay warning threshold must be less than delay critical threshold")
        _logger.error("Warning delay: %s", args.delay_warning)
        _logger.error("Critical delay: %s", args.delay_critical)
        sys.exit(Status.UNKNOWN.value)
    _logger.debug("Starting Patroni Monitoring CLI")
    uri = args.url.rstrip('/')
    _logger.debug(f"Using Patroni API URL: {uri}")
    lag = {
        'warning': args.warning,
        'critical': args.critical
    }
    _logger.debug("Using replication lag thresholds: %s", lag)
    patroni_api = PatroniAPI(
        url=uri,
        timeout=args.conn_timeout)
    status = patroni_api.cluster_status(lag=lag)
    _logger.info("Cluster scope: %s", patroni_api.scope)
    _logger.info(tabulate.tabulate(status, headers="keys"))
    monitoring = Monitoring(
        results=status,
    )
    sys.exit(monitoring.status)