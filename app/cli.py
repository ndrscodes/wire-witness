import argparse


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="wirewitness",
        description="WireWitness - Network performance monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default environment variable configuration
  python main.py

  # Override specific settings
  python main.py --influx-host http://influx:8086 --influx-org myorg

  # Override iperf3 settings
  python main.py --iperf-host 192.168.1.100 --iperf-schedule "*/5 * * * *"

  # Test configuration without starting scheduler
  python main.py --dry-run

  # Increase logging verbosity
  python main.py --log-level DEBUG
        """,
    )

    # Database arguments
    db_group = parser.add_argument_group("Database Configuration")
    db_group.add_argument(
        "--influx-host",
        help="InfluxDB host URL (default: INFLUXDB_HOST env var)",
    )
    db_group.add_argument(
        "--influx-org",
        help="InfluxDB organization name (default: INFLUXDB_ORG env var)",
    )
    db_group.add_argument(
        "--influx-database",
        default=None,
        help="InfluxDB database/bucket name (default: INFLUXDB_DATABASE env var or 'wirewitness')",
    )
    db_group.add_argument(
        "--influx-token",
        help="InfluxDB authentication token (default: INFLUXDB_TOKEN env var)",
    )
    db_group.add_argument(
        "--influx-token-file",
        help="Path to file containing InfluxDB token (default: INFLUXDB_TOKEN_FILE env var)",
    )
    db_group.add_argument(
        "--max-retry-time",
        default=None,
        type=int,
        help="Maximum retry time (ms) for failed tests in seconds (default: MAX_RETRY_TIME env var or 60 * 60 * 24 * 1000)",
    )
    db_group.add_argument(
        "--max-retry-delay",
        default=None,
        type=int,
        help="Maximum delay (ms) between retries (default: MAX_RETRY_DELAY env var or 120000)",
    )
    db_group.add_argument(
        "--retry-interval",
        default=None,
        type=int,
        help="Maximum retry time (ms) for failed tests in seconds (default: RETRY_INTERVAL env var or 5000)",
    )

    # iperf3 arguments
    iperf_group = parser.add_argument_group("iperf3 Settings")
    iperf_group.add_argument(
        "--iperf-cmd",
        help="Path to iperf3 binary (default: IPERF_CMD env var)",
    )
    iperf_group.add_argument(
        "--iperf-host",
        help="Target host for iperf3 tests (default: IPERF_TARGET_HOST env var)",
    )
    iperf_group.add_argument(
        "--iperf-duration",
        type=int,
        help="Test duration in seconds (default: IPERF_DURATION env var or 10)",
    )
    iperf_group.add_argument(
        "--iperf-schedule",
        help="Cron schedule for iperf3 tests (default: IPERF_CRON_SCHEDULE env var)",
    )

    # speedtest arguments
    speedtest_group = parser.add_argument_group("speedtest Settings")
    speedtest_group.add_argument(
        "--speedtest-cmd",
        help="Path to speedtest binary (default: SPEEDTEST_CMD env var)",
    )
    speedtest_group.add_argument(
        "--speedtest-schedule",
        help="Cron schedule for speedtest tests (default: SPEEDTEST_CRON_SCHEDULE env var)",
    )
    speedtest_group.add_argument(
        "--accept-speedtest-gdpr",
        action="store_true",
        default=False,
        help="Accept speedtest GDPR terms (default: SPEEDTEST_GDPR_ACCEPT env var)",
    )
    speedtest_group.add_argument(
        "--accept-speedtest-license",
        action="store_true",
        default=False,
        help="Accept speedtest license terms (default: SPEEDTEST_LICENSE_ACCEPT env var)",
    )

    ping_group = parser.add_argument_group("ping Settings")
    ping_group.add_argument(
        "--ping-cmd",
        help="Path to ping binary (default: PING_CMD env var)",
    )
    ping_group.add_argument(
        "--ping-host",
        help="Target host for ping tests (default: PING_TARGET_HOST env var)",
    )
    ping_group.add_argument(
        "--ping-count",
        type=int,
        help="Number of ping packets to send (default: PING_COUNT env var or 5)",
    )
    ping_group.add_argument(
        "--ping-schedule",
        help="Cron schedule for ping tests (default: PING_CRON_SCHEDULE env var)",
    )

    # Scheduler configuration arguments
    sched_group = parser.add_argument_group("Scheduler Configuration")
    sched_group.add_argument(
        "--misfire-grace-time",
        type=int,
        help="Grace time for missed jobs in seconds (default: MISFIRE_GRACE_TIME env var)",
    )

    # Utility arguments
    util_group = parser.add_argument_group("Utility Arguments")
    util_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without starting scheduler",
    )
    util_group.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Logging level (default: INFO)",
    )
    util_group.add_argument(
        "--version",
        action="version",
        version="wirewitness 0.1.0",
    )
    util_group.add_argument(
        "--config-file",
        help="Path to configuration file (default: WIREWITNESS_CONFIG_FILE env var)",
        default=None,
    )

    return parser


def parse_args(args=None):
    """Parse command-line arguments.

    Args:
        args: Optional list of arguments to parse. If None, uses sys.argv.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = create_parser()
    return parser.parse_args(args)
