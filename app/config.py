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
        self.errors: list[str] = []
    
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
class FromDictMixin:
    @classmethod
    def from_dict(cls, data: dict) -> Self:
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
class PingTask(Schedulable, SupportsMerge["PingTask"], ValidationMixin, NamedMixin, FromDictMixin):
    target_host: str
    count: int = 5

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            schedule=data.get("schedule"),
            target_host=data["target_host"],
            count=data.get("count", 5),
        )

    @classmethod
    def from_env(cls) -> Self | None:
        target_host = os.environ.get("PING_TARGET_HOST")
        count = int(os.environ.get("PING_COUNT", "5"))
        schedule = os.environ.get("PING_CRON_SCHEDULE")
        if target_host and count > 0 and schedule:
            return cls(schedule, target_host, count)
        return None
    
    @classmethod
    def from_cli_args(cls, args) -> Self | None:
        target_host = args.ping_host
        count = args.ping_count if args.ping_count is not None else 5
        schedule = args.ping_schedule
        if target_host and count > 0 and schedule:
            return cls(schedule, target_host, count)
        return None
        
    def merge_with(self, other: Self | None) -> Self:
        if other is None:
            return self
        
        if other.target_host is not None:
            self.target_host = other.target_host
        if other.count is not None and other.count > 0:
            self.count = other.count
        if other.schedule is not None:
            self.schedule = other.schedule

        return self
    
    def validate(self) -> ValidationResult:
        result = ValidationResult()
        if not self.target_host:
            result.add_error("ping host is required")
        if not self.count or self.count <= 0:
            result.add_error("ping count must be greater than 0")
        return result
    
    def name(self) -> str:
        return f"ping-{self.target_host}"

@dataclass
class PingConfig(SupportsMerge["PingConfig"], ValidationMixin, FromDictMixin):
    DEFAULT_CMD = which("ping")
    cmd: str | None = DEFAULT_CMD
    tasks: list[PingTask] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            cmd=data.get("cmd", which("ping")),
            tasks=[PingTask.from_dict(t) for t in data.get("tasks", [])],
        )
    
    @classmethod
    def from_env(cls) -> Self | None:
        cmd = os.environ.get("PING_CMD") or cls.DEFAULT_CMD
        task = PingTask.from_env()
        if task:
            return cls(cmd=cmd, tasks=[task])
        return cls(cmd)
    
    @classmethod
    def from_cli_args(cls, args) -> Self | None:
        cmd = args.ping_cmd or cls.DEFAULT_CMD
        task = PingTask.from_cli_args(args)
        if task:
            return cls(cmd=cmd, tasks=[task])
        return cls(cmd)
    
    def merge_with(self, other: Self | None) -> Self:
        if other is None:
            return self
        
        if other.cmd is not None:
            self.cmd = other.cmd
        if other.tasks:
            self.tasks.extend(other.tasks)

        return self
    
    def validate(self) -> ValidationResult:
        res = ValidationResult()

        if not self.cmd:
            res.add_error("binary not found or not configured.")
        for i, task in enumerate(self.tasks):
            val = task.validate()
            if not val.valid:
                for e in val.errors:
                    res.add_error(f"task {i}: {e}")

        return res

@dataclass
class IPerfTask(Schedulable, SupportsMerge["IPerfTask"], ValidationMixin, NamedMixin):
    target_host: str
    duration: int = 10
    additional_flags: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "IPerfTask":
        return cls(
            schedule=data.get("schedule"),
            target_host=data["target_host"],
            duration=data.get("duration", 10),
            additional_flags=data.get("additional_flags", ""),
        )

    @classmethod
    def from_env(cls) -> "IPerfTask | None":
        cmd = os.environ.get("IPERF_CMD") or which("iperf3")
        target_host = os.environ.get("IPERF_TARGET_HOST")
        duration = int(os.environ.get("IPERF_DURATION", "10"))
        schedule = os.environ.get("IPERF_CRON_SCHEDULE")
        additional_flags = os.environ.get("IPERF_ADDITIONAL_FLAGS", "")
        if cmd and target_host and duration > 0 and schedule:
            return IPerfTask(schedule, target_host, duration, additional_flags)
        return None
    
    @staticmethod
    def from_cli_args(args) -> "IPerfTask | None":
        target_host = args.iperf_host
        duration = args.iperf_duration if args.iperf_duration is not None else 10
        schedule = args.iperf_schedule
        if target_host and duration > 0 and schedule:
            return IPerfTask(schedule, target_host, duration)
        return None
    
    def merge_with(self, other: "IPerfTask | None") -> "IPerfTask":
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
class IPerfConfig(SupportsMerge["IPerfConfig"], ValidationMixin, NamedMixin):
    DEFAULT_CMD = which("iperf3")
    cmd: str | None = DEFAULT_CMD
    tasks: list[IPerfTask] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "IPerfConfig":
        return cls(
            cmd=data.get("cmd", which("iperf3")),
            tasks=[IPerfTask.from_dict(t) for t in data.get("tasks", [])],
        )
    
    @classmethod
    def from_env(cls) -> "IPerfConfig | None":
        cmd = os.environ.get("IPERF_CMD") or which("iperf3")
        task = IPerfTask.from_env()
        if task:
            return IPerfConfig(cmd=cmd, tasks=[task])
        return IPerfConfig(cmd)
    
    @classmethod
    def from_cli_args(cls, args) -> "IPerfConfig | None":
        cmd = args.iperf_cmd or which("iperf3")
        task = IPerfTask.from_cli_args(args)
        if task:
            return IPerfConfig(cmd=cmd, tasks=[task])
        return IPerfConfig(cmd)
    
    def merge_with(self, other: Self | None) -> Self:
        if not other:
            return self
        self.cmd = other.cmd if other else None or self.cmd
        self.tasks += other.tasks
        return self
    
    def validate(self) -> ValidationResult:
        res = ValidationResult()
        if not self.cmd:
            res.add_error("IPerf command is required.")
        for i, task in enumerate(self.tasks):
            val = task.validate()
            if not val.valid:
                for e in val.errors:
                    res.add_error(f"task {i}: {e}")

        return res

@dataclass
class SpeedtestTask(Schedulable, SupportsMerge["SpeedtestTask"], ValidationMixin, NamedMixin):
    additional_flags: str = ""
    id: str = "speedtest"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            schedule=data.get("schedule"),
            additional_flags=data.get("additional_flags", ""),
            id=data.get("id", "speedtest"),
        )

    @staticmethod
    def from_env() -> "SpeedtestTask | None":
        cmd = os.environ.get("SPEEDTEST_CMD") or which("speedtest")
        schedule = os.environ.get("SPEEDTEST_CRON_SCHEDULE")
        additional_flags = os.environ.get("SPEEDTEST_ADDITIONAL_FLAGS") or ""
        if cmd and schedule:
            return SpeedtestTask(schedule, additional_flags, "speedtest")
        return None
    
    @staticmethod
    def from_cli_args(args) -> "SpeedtestTask | None":
        cmd = args.speedtest_cmd or which("speedtest")
        schedule = args.speedtest_schedule
        if cmd and schedule:
            return SpeedtestTask(schedule, "", "speedtest")
        return None
    
    def merge_with(self, other: "SpeedtestTask | None") -> "SpeedtestTask":
        if other is None:
            return self

        if other.schedule is not None:
            self.schedule = other.schedule
        return self
    
    def validate(self) -> ValidationResult:
        result = ValidationResult()
        if not self.schedule:
            result.add_error("Schedule is required.")
        return result
    
    def name(self) -> str:
        return self.id

@dataclass
class SpeedtestConfig(SupportsMerge["SpeedtestConfig"], ValidationMixin):
    DEFAULT_CMD = which("speedtest")
    cmd: str | None = DEFAULT_CMD
    tasks: list[SpeedtestTask] = field(default_factory=list)
    accept_gdpr: bool = False
    accept_license: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        tasks = [SpeedtestTask.from_dict(task_data) for task_data in data.get("tasks", [])]
        cmd = data.get("cmd") or cls.DEFAULT_CMD
        accept_gdpr = str(data.get("accept_gdpr")).lower() in YES_VALUES
        accept_license = str(data.get("accept_license")).lower() in YES_VALUES
        return cls(cmd, tasks, accept_gdpr, accept_license)

    @classmethod
    def from_env(cls) -> Self | None:
        cmd = os.environ.get("SPEEDTEST_CMD", cls.DEFAULT_CMD)
        task = SpeedtestTask.from_env()
        accept_gdpr = True if SPEEDTEST_GDPR_ACCEPT_ENV in os.environ and os.environ.get(SPEEDTEST_GDPR_ACCEPT_ENV, "").lower() in YES_VALUES else False
        accept_license = True if SPEEDTEST_LIC_ACCEPT_ENV in os.environ and os.environ.get(SPEEDTEST_LIC_ACCEPT_ENV, "").lower() in YES_VALUES else False
        if task is not None:
            return cls(cmd, [task], accept_gdpr, accept_license)
        return cls(cmd, [], accept_gdpr, accept_license)
    
    @classmethod
    def from_cli_args(cls, args) -> Self | None:
        cmd = args.speedtest_cmd or cls.DEFAULT_CMD
        task = SpeedtestTask.from_cli_args(args)
        accept_gdpr = args.accept_speedtest_gdpr is not None and args.accept_speedtest_gdpr
        accept_license = args.accept_speedtest_license is not None and args.accept_speedtest_license
        if task is not None:
            return cls(cmd, [task], accept_gdpr, accept_license)
        return cls(cmd, [], accept_gdpr, accept_license)
    
    def merge_with(self, other: Self | None) -> Self:
        if other is None:
            return self
        
        if other.cmd is not None:
            self.cmd = other.cmd
        if other.tasks:
            self.tasks.extend(other.tasks)
        
        # special case here: only merge if the other side is accepted
        if other.accept_gdpr:
            self.accept_gdpr = other.accept_gdpr
        if other.accept_license:
            self.accept_license = other.accept_license
        return self
    
    def validate(self) -> ValidationResult:
        result = ValidationResult()
        if not self.cmd:
            result.add_error("Speedtest command is required.")
        if not self.tasks:
            result.add_error("At least one speedtest task is required.")
        if not self.accept_gdpr:
            result.add_error("GDPR acceptance is required.")
        if not self.accept_license:
            result.add_error("License acceptance is required.")
        for task in self.tasks:
            task_result = task.validate()
            if task_result.errors:
                for error in task_result.errors:
                    result.add_error(f"Speedtest task {task.name()} - {error}")
        return result

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
    def from_dict(cls, data: dict) -> Self:
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

    @classmethod
    def from_env(cls) -> Self | None:
        host = os.environ.get("INFLUXDB_HOST")
        org = os.environ.get("INFLUXDB_ORG")
        database = os.environ.get("INFLUXDB_DATABASE", "wirewitness")
        token_file = os.environ.get("INFLUXDB_TOKEN_FILE")
        token = load_token_from_file(token_file) if token_file else os.environ.get("INFLUXDB_TOKEN")
        retry_interval = int(os.environ.get("RETRY_INTERVAL", "5000"))
        max_retry_time = int(os.environ.get("MAX_RETRY_TIME", str(60 * 60 * 24 * 1000)))
        max_retry_delay = int(os.environ.get("MAX_RETRY_DELAY", "120000"))

        if host and org and token:
            return cls(host, org, database, token_file, token, retry_interval, max_retry_time, max_retry_delay)
        return None
    
    @classmethod
    def from_cli_args(cls, args) -> Self | None:
        host = args.influx_host
        org = args.influx_org
        database = args.influx_database or "wirewitness"
        token_file = args.influx_token_file
        token = load_token_from_file(token_file) if token_file else args.influx_token
        retry_interval = args.retry_interval if args.retry_interval is not None else 5000
        max_retry_time = args.max_retry_time if args.max_retry_time is not None else 60 * 60 * 24 * 1000
        max_retry_delay = args.max_retry_delay if args.max_retry_delay is not None else 120000

        if host and org and token:
            return cls(host, org, database, token_file, token, retry_interval, max_retry_time, max_retry_delay)
        return None
    
    def merge_with(self, other: Self | None) -> Self:
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
    ping: PingConfig | None = None
    iperf: IPerfConfig | None = None
    speedtest: SpeedtestConfig | None = None
    grace_time: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        config = cls()
        
        # Parse InfluxDB config
        if "influx" in data:
            config.influx = InfluxConfig.from_dict(data["influx"])
        
        if "ping" in data:
            config.ping = PingConfig.from_dict(data["ping"])

        if "iperf" in data:
            config.iperf = IPerfConfig.from_dict(data["iperf"])

        if "speedtest" in data:
            config.speedtest = SpeedtestConfig.from_dict(data["speedtest"])
        
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

        if env_ping or cli_ping:
            ping = merge(env_ping, cli_ping)
            self.ping = merge(self.ping, ping)
        if env_influx or cli_influx:
            influx = merge(env_influx, cli_influx)
            self.influx = merge(self.influx, influx)
        if env_iperf or cli_iperf:
            iperf = merge(env_iperf, cli_iperf)
            self.iperf = merge(self.iperf, iperf)
        if env_speedtest or cli_speedtest:
            speedtest = merge(env_speedtest, cli_speedtest)
            self.speedtest = merge(self.speedtest, speedtest)

    def validate(self) -> ValidationResult:
        res = ValidationResult()

        if self.ping:
            for e in self.ping.validate().errors:
                res.add_error(f"ping: {e}")
        if self.iperf:
            for e in self.iperf.validate().errors:
                res.add_error(f"iperf: {e}")
        if self.speedtest:
            for e in self.speedtest.validate().errors:
                res.add_error(f"speedtest: {e}")
        if self.influx:
            for e in self.influx.validate().errors:
                res.add_error(f"influx: {e}")
        
        return res

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
