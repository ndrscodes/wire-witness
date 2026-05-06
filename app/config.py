import os
import json
import yaml
from dataclasses import dataclass, field
from shutil import which
from typing import Self, TypeVar, Generic, Any

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

def parse_bool(value: Any) -> bool:
    """Parse a boolean value from various representations."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in YES_VALUES
    return bool(value)

T = TypeVar("T", bound="SupportsMerge")

class ValidationResult:
    def __init__(self) -> None:
        self.valid = True
        self.errors = []
    
    def add_error(self, error: str) -> None:
        self.valid = False
        self.errors.append(error)

    def __str__(self) -> str:
        return f"valid={self.valid}, errors={self.errors}"

class ValidationMixin:
    def validate(self) -> ValidationResult:
        raise NotImplementedError

class NamedMixin:
    def name(self) -> str:
        raise NotImplementedError

@dataclass
class SupportsMerge(Generic[T]):
    def merge_with(self, other: T | None) -> T:
        raise NotImplementedError

def merge(a: T | None, b: T | None) -> T | None:
    if a is None:
        return b
    if b is None:
        return a
    return a.merge_with(b)

@dataclass
class Schedulable:
    schedule: str | None

    def get_schedule(self) -> str | None:
        return self.schedule

@dataclass
class PingConfig(Schedulable, SupportsMerge["PingConfig"], ValidationMixin, NamedMixin):
    target_host: str
    count: int = 5
    cmd: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "PingConfig":
        return cls(
            schedule=data.get("schedule"),
            target_host=data["target_host"],
            count=data.get("count", 5),
            cmd=data.get("cmd", which("ping")),
        )

    @staticmethod
    def from_env() -> "PingConfig | None":
        cmd = os.environ.get("PING_CMD") or which("ping")
        target_host = os.environ.get("PING_TARGET_HOST")
        count = int(os.environ.get("PING_COUNT", "5"))
        schedule = os.environ.get("PING_CRON_SCHEDULE")
        if cmd and target_host and count > 0 and schedule:
            return PingConfig(schedule, target_host, count, cmd)
        return None
    
    @staticmethod
    def from_cli_args(args) -> "PingConfig | None":
        cmd = args.ping_cmd or which("ping")
        target_host = args.ping_host
        count = args.ping_count if args.ping_count is not None else 5
        schedule = args.ping_schedule
        if cmd and target_host and count > 0 and schedule:
            return PingConfig(schedule, target_host, count, cmd)
        return None
        
    def merge_with(self, other: "PingConfig | None") -> "PingConfig":
        if other is None:
            return self
        
        if other.cmd is not None:
            self.cmd = other.cmd
        if other.target_host is not None:
            self.target_host = other.target_host
        if other.count is not None and other.count > 0:
            self.count = other.count
        if other.schedule is not None:
            self.schedule = other.schedule
        return self
    
    def validate(self) -> ValidationResult:
        result = ValidationResult()
        if not self.cmd:
            result.add_error("ping cmd is required")
        if not self.target_host:
            result.add_error("ping host is required")
        if not self.count or self.count <= 0:
            result.add_error("ping count must be greater than 0")
        return result
    
    def name(self) -> str:
        return f"ping-{self.target_host}"

@dataclass
class IPerfConfig(Schedulable, SupportsMerge["IPerfConfig"], ValidationMixin, NamedMixin):
    target_host: str
    duration: int = 10
    additional_flags: str = ""
    cmd: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "IPerfConfig":
        return cls(
            schedule=data.get("schedule"),
            target_host=data["target_host"],
            duration=data.get("duration", 10),
            additional_flags=data.get("additional_flags", ""),
            cmd=data.get("cmd", which("iperf3")),
        )

    @staticmethod
    def from_env() -> "IPerfConfig | None":
        cmd = os.environ.get("IPERF_CMD") or which("iperf3")
        target_host = os.environ.get("IPERF_TARGET_HOST")
        duration = int(os.environ.get("IPERF_DURATION", "10"))
        schedule = os.environ.get("IPERF_CRON_SCHEDULE")
        additional_flags = os.environ.get("IPERF_ADDITIONAL_FLAGS", "")
        if cmd and target_host and duration > 0 and schedule:
            return IPerfConfig(schedule, target_host, duration, additional_flags, cmd)
        return None
    
    @staticmethod
    def from_cli_args(args) -> "IPerfConfig | None":
        cmd = args.iperf_cmd or which("iperf3")
        target_host = args.iperf_host
        duration = args.iperf_duration if args.iperf_duration is not None else 10
        schedule = args.iperf_schedule
        if cmd and target_host and duration > 0 and schedule:
            return IPerfConfig(schedule, target_host, duration, cmd)
        return None
    
    def merge_with(self, other: "IPerfConfig | None") -> "IPerfConfig":
        if not other:
            return self
        
        if other.cmd is not None:
            self.cmd = other.cmd
        if other.target_host is not None:
            self.target_host = other.target_host
        if other.duration is not None and other.duration > 0:
            self.duration = other.duration
        if other.schedule is not None:
            self.schedule = other.schedule
        return self
    
    def validate(self) -> ValidationResult:
        result = ValidationResult()
        if not self.cmd:
            result.errors.append("IPerf command is required.")
        if not self.target_host:
            result.errors.append("Target host is required.")
        if self.duration <= 0:
            result.errors.append("Duration must be greater than zero.")
        if not self.schedule:
            result.errors.append("Schedule is required.")
        return result
    
    def name(self) -> str:
        return f"iperf-{self.target_host}"

@dataclass
class SpeedtestConfig(Schedulable, SupportsMerge["SpeedtestConfig"], ValidationMixin, NamedMixin):
    accept_license: bool = False
    accept_gdpr: bool = False
    additional_flags: str = ""
    id: str = "speedtest"
    cmd: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "SpeedtestConfig":
        return cls(
            schedule=data.get("schedule"),
            accept_license=parse_bool(data.get("accept_license", False)),
            accept_gdpr=parse_bool(data.get("accept_gdpr", False)),
            additional_flags=data.get("additional_flags", ""),
            id=data.get("id", "speedtest"),
            cmd=data.get("cmd", which("speedtest")),
        )

    @staticmethod
    def from_env() -> "SpeedtestConfig | None":
        cmd = os.environ.get("SPEEDTEST_CMD") or which("speedtest")
        schedule = os.environ.get("SPEEDTEST_CRON_SCHEDULE")
        accept_license = True if SPEEDTEST_LIC_ACCEPT_ENV in os.environ and os.environ.get(SPEEDTEST_LIC_ACCEPT_ENV, "").lower() in YES_VALUES else False
        accept_gdpr = True if SPEEDTEST_GDPR_ACCEPT_ENV in os.environ and os.environ.get(SPEEDTEST_GDPR_ACCEPT_ENV, "").lower() in YES_VALUES else False
        additional_flags = os.environ.get("SPEEDTEST_ADDITIONAL_FLAGS") or ""
        if cmd and schedule and accept_license and accept_gdpr:
            return SpeedtestConfig(schedule, accept_license, accept_gdpr, additional_flags, "speedtest", cmd)
        return None
    
    @staticmethod
    def from_cli_args(args) -> "SpeedtestConfig | None":
        cmd = args.speedtest_cmd or which("speedtest")
        schedule = args.speedtest_schedule
        accept_license = args.speedtest_license is not None and args.speedtest_license
        accept_gdpr = args.speedtest_gdpr is not None and args.speedtest_gdpr
        if cmd and schedule and accept_license and accept_gdpr:
            return SpeedtestConfig(schedule, accept_license, accept_gdpr, "", "speedtest", cmd)
        return None
    
    def merge_with(self, other: "SpeedtestConfig | None") -> "SpeedtestConfig":
        if other is None:
            return self
        
        if other.cmd is not None:
            self.cmd = other.cmd
        if other.accept_license:
            self.accept_license = other.accept_license
        if other.accept_gdpr:
            self.accept_gdpr = other.accept_gdpr
        if other.schedule is not None:
            self.schedule = other.schedule
        return self
    
    def validate(self) -> ValidationResult:
        result = ValidationResult()
        if not self.cmd:
            result.add_error("Speedtest command is required.")
        if not self.accept_license:
            result.add_error("License agreement must be accepted.")
        if not self.accept_gdpr:
            result.add_error("GDPR agreement must be accepted.")
        return result
    
    def name(self) -> str:
        return self.id

@dataclass
class InfluxConfig(SupportsMerge["InfluxConfig"], ValidationMixin):
    host: str
    org: str
    database: str
    token_file: str | None = None
    token: str | None = None
    retry_interval: int = 5000
    max_retry_time: int = 60 * 60 * 24 * 1000
    max_retry_delay: int = 120000

    @classmethod
    def from_dict(cls, data: dict) -> "InfluxConfig":
        token_file = data.get("token_file")
        token = None
        if token_file:
            token = load_token_from_file(token_file)
        if not token:
            token = data.get("token")
        return cls(
            host=data["host"],
            org=data["org"],
            database=data.get("database", "wirewitness"),
            token_file=token_file,
            token=token,
            retry_interval=data.get("retry_interval", 5000),
            max_retry_time=data.get("max_retry_time", 60 * 60 * 24 * 1000),
            max_retry_delay=data.get("max_retry_delay", 120000),
        )

    @staticmethod
    def from_env() -> "InfluxConfig | None":
        host = os.environ.get("INFLUXDB_HOST")
        org = os.environ.get("INFLUXDB_ORG")
        database = os.environ.get("INFLUXDB_DATABASE", "wirewitness")
        token_file = os.environ.get("INFLUXDB_TOKEN_FILE")
        token = load_token_from_file(token_file) if token_file else os.environ.get("INFLUXDB_TOKEN")
        retry_interval = int(os.environ.get("RETRY_INTERVAL", "5000"))
        max_retry_time = int(os.environ.get("MAX_RETRY_TIME", str(60 * 60 * 24 * 1000)))
        max_retry_delay = int(os.environ.get("MAX_RETRY_DELAY", "120000"))

        if host and org and token:
            return InfluxConfig(host, org, database, token_file, token, retry_interval, max_retry_time, max_retry_delay)
        return None
    
    @staticmethod
    def from_cli_args(args) -> "InfluxConfig | None":
        host = args.influx_host
        org = args.influx_org
        database = args.influx_database or "wirewitness"
        token_file = args.influx_token_file
        token = load_token_from_file(token_file) if token_file else args.influx_token
        retry_interval = args.retry_interval if args.retry_interval is not None else 5000
        max_retry_time = args.max_retry_time if args.max_retry_time is not None else 60 * 60 * 24 * 1000
        max_retry_delay = args.max_retry_delay if args.max_retry_delay is not None else 120000

        if host and org and token:
            return InfluxConfig(host, org, database, token_file, token, retry_interval, max_retry_time, max_retry_delay)
        return None
    
    def merge_with(self, other: "InfluxConfig | None") -> "InfluxConfig":
        if other is None:
            return self
        
        if other.host is not None:
            self.host = other.host
        if other.org is not None:
            self.org = other.org
        if other.database is not None:
            self.database = other.database
        if other.token is not None:
            self.token = other.token
        if other.retry_interval is not None:
            self.retry_interval = other.retry_interval
        if other.max_retry_time is not None:
            self.max_retry_time = other.max_retry_time
        if other.max_retry_delay is not None:
            self.max_retry_delay = other.max_retry_delay
        return self
    
    def validate(self) -> ValidationResult:
        result = ValidationResult()
        if not self.host:
            result.add_error("InfluxDB host is required")
        if not self.org:
            result.add_error("InfluxDB organization is required")
        if not self.database:
            result.add_error("InfluxDB database is required")
        if not self.token:
            result.add_error("InfluxDB token is required")
        return result

@dataclass
class Config(ValidationMixin):
    influx: InfluxConfig | None = None
    ping: list[PingConfig] = field(default_factory=list)
    iperf: list[IPerfConfig] = field(default_factory=list)
    speedtest: list[SpeedtestConfig] = field(default_factory=list)
    grace_time: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        config = cls()
        
        # Parse InfluxDB config
        if "influx" in data:
            config.influx = InfluxConfig.from_dict(data["influx"])
        
        # Parse ping configs (list)
        for ping_data in data.get("ping", []):
            config.ping.append(PingConfig.from_dict(ping_data))
        
        # Parse iperf configs (list)
        for iperf_data in data.get("iperf", []):
            config.iperf.append(IPerfConfig.from_dict(iperf_data))
        
        # Parse speedtest configs (list)
        for speedtest_data in data.get("speedtest", []):
            config.speedtest.append(SpeedtestConfig.from_dict(speedtest_data))
        
        # Parse grace_time
        config.grace_time = data.get("grace_time")
        
        return config

    def load(self, args):
        os_grace = os.environ.get("MISFIRE_GRACE_TIME", None)
        self.grace_time = args.get("grace_time", None) or int(os_grace) if os_grace else None

        env_ping = PingConfig.from_env()
        env_iperf = IPerfConfig.from_env()
        env_speedtest = SpeedtestConfig.from_env()
        env_influx = InfluxConfig.from_env()

        cli_ping = PingConfig.from_cli_args(args)
        cli_iperf = IPerfConfig.from_cli_args(args)
        cli_speedtest = SpeedtestConfig.from_cli_args(args)
        cli_influx = InfluxConfig.from_cli_args(args)

        ping = merge(env_ping, cli_ping)
        iperf = merge(env_iperf, cli_iperf)
        speedtest = merge(env_speedtest, cli_speedtest)
        influx = merge(env_influx, cli_influx)
        influx = merge(self.influx, influx)

        if ping is not None:
            self.ping.append(ping)
        if iperf is not None:
            self.iperf.append(iperf)
        if speedtest is not None:
            self.speedtest.append(speedtest)
        if influx is not None:
            self.influx = influx

    def validate(self) -> ValidationResult:
        result = ValidationResult()
        if len(self.ping) == 0:
            result.add_error("No ping configuration provided.")
        if len(self.iperf) == 0:
            result.add_error("No iperf configuration provided.")
        if len(self.speedtest) == 0:
            result.add_error("No speedtest configuration provided.")
        if self.influx is None:
            result.add_error("No influx configuration provided.")
        
        for i, ping in enumerate(self.ping):
            res = ping.validate()
            if not res.valid:
                result.add_error(f"ping[{i}] {res}")
        for i, iperf in enumerate(self.iperf):
            res = iperf.validate()
            if not res.valid:
                result.add_error(f"iperf[{i}] {res}")
        for i, speedtest in enumerate(self.speedtest):
            res = speedtest.validate()
            if not res.valid:
                result.add_error(f"speedtest[{i}] {res}")
        
        return result


class ConfigLoader:
    """Loads configuration from YAML files into Config objects."""
    
    @staticmethod
    def load_file(path: str) -> Config:
        """Load configuration from a YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        if data is None:
            return Config()
        if not isinstance(data, dict):
            raise ValueError("Configuration file must contain a YAML mapping")
        return Config.from_dict(data)
