import os
import json

# I think more config formats should allow stuff like "yeah" or "certainly" as "true". Just makes config more friendly :)
YES_VALUES = ["true", "1", "yes", "y", "certainly", "yeah", "yup"]
SPEEDTEST_LIC_ACCEPT_ENV = "SPEEDTEST_LICENSE_ACCEPT"
SPEEDTEST_GDPR_ACCEPT_ENV = "SPEEDTEST_GDPR_ACCEPT"

def read_secret_file(path: str) -> str | None:
    if path and os.path.isfile(path):
        with open(path, "r") as f:
            return f.read().strip()
    return None


def load_token_from_file(token_file: str | None) -> str | None:
    if token_file is None:
        return None
    content = read_secret_file(token_file)
    if content is None:
        return None
    try:
        return json.loads(content).get("token")
    except (json.JSONDecodeError, AttributeError, TypeError):
        return None


class Config:
    INFLUXDB_HOST: str | None = os.environ.get("INFLUXDB_HOST")
    INFLUXDB_ORG: str | None = os.environ.get("INFLUXDB_ORG")
    INFLUXDB_DATABASE: str = os.environ.get("INFLUXDB_DATABASE", "wirewitness")

    INFLUXDB_TOKEN_FILE: str = os.environ.get(
        "INFLUXDB_TOKEN_FILE", "/run/secrets/influx-admin-token"
    )
    INFLUXDB_TOKEN: str | None = (
        load_token_from_file(INFLUXDB_TOKEN_FILE)
        or os.environ.get("INFLUXDB_TOKEN")
    )

    IPERF_CRON_SCHEDULE: str | None = os.environ.get("IPERF_CRON_SCHEDULE")
    SPEEDTEST_CRON_SCHEDULE: str | None = os.environ.get("SPEEDTEST_CRON_SCHEDULE")

    MISFIRE_GRACE_TIME: int | None = (
        int(os.environ.get("MISFIRE_GRACE_TIME", "0"))
        if os.environ.get("MISFIRE_GRACE_TIME")
        else None
    )

    IPERF_CMD: str | None = os.environ.get("IPERF_CMD") or None
    IPERF_TARGET_HOST: str | None = os.environ.get("IPERF_TARGET_HOST")
    IPERF_DURATION: int = int(os.environ.get("IPERF_DURATION", "10"))

    SPEEDTEST_CMD: str | None = os.environ.get("SPEEDTEST_CMD") or None
    ACCEPT_SPEEDTEST_LICENSE: bool = True if SPEEDTEST_LIC_ACCEPT_ENV in os.environ and os.environ.get(SPEEDTEST_LIC_ACCEPT_ENV, "").lower() in YES_VALUES else False
    ACCEPT_SPEEDTEST_GDPR: bool = True if SPEEDTEST_GDPR_ACCEPT_ENV in os.environ and os.environ.get(SPEEDTEST_GDPR_ACCEPT_ENV, "").lower() in YES_VALUES else False

    IPERF_ADDITIONAL_FLAGS: str = os.environ.get("IPERF_ADDITIONAL_FLAGS", "")
    SPEEDTEST_ADDITIONAL_FLAGS: str = os.environ.get("SPEEDTEST_ADDITIONAL_FLAGS", "")
    
    MAX_RETRY_TIME = int(os.environ.get("MAX_RETRY_TIME", str(60 * 60 * 24 * 1000)))
    MAX_RETRY_DELAY = int(os.environ.get("MAX_RETRY_DELAY", "120000"))
    RETRY_INTERVAL = int(os.environ.get("RETRY_INTERVAL", "5000"))

    @classmethod
    def from_cli_args(cls, args) -> type["Config"]:
        if args.influx_host is not None:
            cls.INFLUXDB_HOST = args.influx_host
        if args.influx_org is not None:
            cls.INFLUXDB_ORG = args.influx_org
        if args.influx_database is not None:
            cls.INFLUXDB_DATABASE = args.influx_database
        if args.influx_token is not None:
            cls.INFLUXDB_TOKEN = args.influx_token
        if args.influx_token_file is not None:
            cls.INFLUXDB_TOKEN_FILE = args.influx_token_file
            cls.INFLUXDB_TOKEN = (
                load_token_from_file(cls.INFLUXDB_TOKEN_FILE)
                or os.environ.get("INFLUXDB_TOKEN")
            )
        if args.max_retry_time is not None:
            cls.MAX_RETRY_TIME = args.max_retry_time
        if args.max_retry_delay is not None:
            cls.MAX_RETRY_DELAY = args.max_retry_delay
        if args.retry_interval is not None:
            cls.RETRY_INTERVAL = args.retry_interval

        if args.iperf_cmd is not None:
            cls.IPERF_CMD = args.iperf_cmd
        if args.iperf_host is not None:
            cls.IPERF_TARGET_HOST = args.iperf_host
        if args.iperf_duration is not None:
            cls.IPERF_DURATION = args.iperf_duration
        if args.iperf_schedule is not None:
            cls.IPERF_CRON_SCHEDULE = args.iperf_schedule

        if args.speedtest_cmd is not None:
            cls.SPEEDTEST_CMD = args.speedtest_cmd
        if args.speedtest_schedule is not None:
            cls.SPEEDTEST_CRON_SCHEDULE = args.speedtest_schedule
        if args.speedtest_gdpr is not None and args.speedtest_gdpr:
            cls.ACCEPT_SPEEDTEST_GDPR = True
        if args.speedtest_license is not None and args.speedtest_license:
            cls.ACCEPT_SPEEDTEST_LICENSE = True

        if args.misfire_grace_time is not None:
            cls.MISFIRE_GRACE_TIME = args.misfire_grace_time
        
        if args.max_retry_time is not None:
            cls.MAX_RETRY_TIME = args.max_retry_time

        return cls

    @classmethod
    def validate(cls) -> list[str]:
        errors = []
        if not cls.INFLUXDB_HOST:
            errors.append("INFLUXDB_HOST is required")
        if not cls.INFLUXDB_ORG:
            errors.append("INFLUXDB_ORG is required")
        if not cls.INFLUXDB_TOKEN:
            errors.append("INFLUXDB_TOKEN is required (set via INFLUXDB_TOKEN or INFLUXDB_TOKEN_FILE)")
        return errors
