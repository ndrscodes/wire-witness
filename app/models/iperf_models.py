from dataclasses import dataclass, field
from typing import Any, Self
from errors import ErrorMixin

@dataclass
class Timestamp:
    time: str = ""
    timesecs: int = 0
    timemillisecs: int = 0

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            time=data.get("time", ""),
            timesecs=data.get("timesecs", 0),
            timemillisecs=data.get("timemillisecs", 0),
        )

@dataclass
class ConnectionInfo:
    socket: int = 0
    local_host: str = ""
    local_port: int = 0
    remote_host: str = ""
    remote_port: int = 0

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            socket=data.get("socket", 0),
            local_host=data.get("local_host", ""),
            local_port=data.get("local_port", 0),
            remote_host=data.get("remote_host", ""),
            remote_port=data.get("remote_port", 0),
        )

@dataclass
class TestStartConfig:
    protocol: str = "TCP"
    num_streams: int = 1
    blksize: int = 4096
    omit: int = 3
    duration: int = 20
    bytes: int = 0
    blocks: int = 0
    reverse: int = 0
    tos: int = 0
    target_bitrate: int = 0
    bidir: int = 0
    fqrate: int = 0
    interval: int = 1
    gso: int = 0
    gro: int = 0

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            protocol=data.get("protocol", "TCP"),
            num_streams=data.get("num_streams", 1),
            blksize=data.get("blksize", 4096),
            omit=data.get("omit", 3),
            duration=data.get("duration", 20),
            bytes=data.get("bytes", 0),
            blocks=data.get("blocks", 0),
            reverse=data.get("reverse", 0),
            tos=data.get("tos", 0),
            target_bitrate=data.get("target_bitrate", 0),
            bidir=data.get("bidir", 0),
            fqrate=data.get("fqrate", 0),
            interval=data.get("interval", 1),
            gso=data.get("gso", 0),
            gro=data.get("gro", 0),
        )

@dataclass
class StartInfo:
    connected: list[ConnectionInfo] = field(default_factory=list)
    version: str = ""
    system_info: str = ""
    timestamp: Timestamp = field(default_factory=Timestamp)
    connecting_to: dict = field(default_factory=dict)
    cookie: str = ""
    tcp_mss_default: int = 0
    target_bitrate: int = 0
    fq_rate: int = 0
    sock_bufsize: int = 0
    snd_buf_actual: int = 0
    rcv_buf_actual: int = 0
    test_start: TestStartConfig = field(default_factory=TestStartConfig)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            connected=[ConnectionInfo.from_dict(c) for c in data.get("connected", [])],
            version=data.get("version", ""),
            system_info=data.get("system_info", ""),
            timestamp=Timestamp.from_dict(data.get("timestamp", {})),
            connecting_to=data.get("connecting_to", {}),
            cookie=data.get("cookie", ""),
            tcp_mss_default=data.get("tcp_mss_default", 0),
            target_bitrate=data.get("target_bitrate", 0),
            fq_rate=data.get("fq_rate", 0),
            sock_bufsize=data.get("sock_bufsize", 0),
            snd_buf_actual=data.get("sndbuf_actual", 0),
            rcv_buf_actual=data.get("rcvbuf_actual", 0),
            test_start=TestStartConfig.from_dict(data.get("test_start", {})),
        )

@dataclass
class StreamIntervalData:
    socket: int = 0
    start: float = 0.0
    end: float = 0.0
    seconds: float = 0.0
    bytes: int = 0
    bits_per_second: float = 0.0
    retransmits: int = 0
    snd_cwnd: int = 0
    snd_wnd: int = 0
    rtt: int = 0
    rttvar: int = 0
    pmtu: int = 0
    reorder: int = 0
    omitted: bool = False
    sender: bool = False

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            socket=data.get("socket", 0),
            start=data.get("start", 0.0),
            end=data.get("end", 0.0),
            seconds=data.get("seconds", 0.0),
            bytes=data.get("bytes", 0),
            bits_per_second=data.get("bits_per_second", 0.0),
            retransmits=data.get("retransmits", 0),
            snd_cwnd=data.get("snd_cwnd", 0),
            snd_wnd=data.get("snd_wnd", 0),
            rtt=data.get("rtt", 0),
            rttvar=data.get("rttvar", 0),
            pmtu=data.get("pmtu", 0),
            reorder=data.get("reorder", 0),
            omitted=data.get("omitted", False),
            sender=data.get("sender", False),
        )

@dataclass
class Sum:
    start: float = 0.0
    end: float = 0.0
    seconds: float = 0.0
    bytes: int = 0
    bits_per_second: float = 0.0
    sender: bool = False

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            start=data.get("start", 0.0),
            end=data.get("end", 0.0),
            seconds=data.get("seconds", 0.0),
            bytes=data.get("bytes", 0),
            bits_per_second=data.get("bits_per_second", 0.0),
            sender=data.get("sender", False),
        )

@dataclass
class SentSum(Sum):
    retransmits: int = 0

    @classmethod
    def from_dict(cls, data):
        return cls(
            start=data.get("start", 0.0),
            end=data.get("end", 0.0),
            seconds=data.get("seconds", 0.0),
            bytes=data.get("bytes", 0),
            bits_per_second=data.get("bits_per_second", 0.0),
            sender=data.get("sender", False),
            retransmits=data.get("retransmits", 0),
        )

@dataclass
class IntervalSum(Sum):
    omitted: bool = False

    @classmethod
    def from_dict(cls, data):
        return cls(
            start=data.get("start", 0.0),
            end=data.get("end", 0.0),
            seconds=data.get("seconds", 0.0),
            bytes=data.get("bytes", 0),
            bits_per_second=data.get("bits_per_second", 0.0),
            sender=data.get("sender", False),
            omitted=data.get("omitted", False),
        )

@dataclass
class Interval:
    streams: list[StreamIntervalData] = field(default_factory=list)
    sum: IntervalSum = field(default_factory=IntervalSum)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            streams=[StreamIntervalData.from_dict(s) for s in data.get("streams", [])],
            sum=IntervalSum.from_dict(data.get("sum", {})),
        )

@dataclass
class StreamEndSender:
    socket: int = 0
    start: float = 0.0
    end: float = 0.0
    seconds: float = 0.0
    bytes: int = 0
    bits_per_second: float = 0.0
    retransmits: int = 0
    reorder: int = 0
    max_snd_cwnd: int = 0
    max_snd_wnd: int = 0
    max_rtt: int = 0
    min_rtt: int = 0
    mean_rtt: int = 0
    sender: bool = False

    @classmethod
    def from_dict(cls, data):
        return cls(
            socket=data.get("socket", 0),
            start=data.get("start", 0.0),
            end=data.get("end", 0.0),
            seconds=data.get("seconds", 0.0),
            bytes=data.get("bytes", 0),
            bits_per_second=data.get("bits_per_second", 0.0),
            retransmits=data.get("retransmits", 0),
            reorder=data.get("reorder", 0),
            max_snd_cwnd=data.get("max_snd_cwnd", 0),
            max_snd_wnd=data.get("max_snd_wnd", 0),
            max_rtt=data.get("max_rtt", 0),
            min_rtt=data.get("min_rtt", 0),
            mean_rtt=data.get("mean_rtt", 0),
            sender=data.get("sender", False),
        )

@dataclass
class StreamEndReceiver:
    socket: int = 0
    start: float = 0.0
    end: float = 0.0
    seconds: float = 0.0
    bytes: int = 0
    bits_per_second: float = 0.0
    sender: bool = False

    @classmethod
    def from_dict(cls, data):
        return cls(
            socket=data.get("socket", 0),
            start=data.get("start", 0.0),
            end=data.get("end", 0.0),
            seconds=data.get("seconds", 0.0),
            bytes=data.get("bytes", 0),
            bits_per_second=data.get("bits_per_second", 0.0),
            sender=data.get("sender", False),
        )

@dataclass
class StreamEnd:
    sender: StreamEndSender = field(default_factory=StreamEndSender)
    receiver: StreamEndReceiver = field(default_factory=StreamEndReceiver)

    @classmethod
    def from_dict(cls, data):
        return cls(
            sender=StreamEndSender.from_dict(data.get("sender", {})),
            receiver=StreamEndReceiver.from_dict(data.get("receiver", {})),
        )

@dataclass
class EndInfo:
    streams: list[StreamEnd] = field(default_factory=list)
    sum_sent: SentSum = field(default_factory=SentSum)
    sum_received: Sum = field(default_factory=Sum)
    cpu_utilization_percent: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            streams=[StreamEnd.from_dict(s) for s in data.get("streams", [])],
            sum_sent=SentSum.from_dict(data.get("sum_sent", {})),
            sum_received=Sum.from_dict(data.get("sum_received", {})),
            cpu_utilization_percent=data.get("cpu_utilization_percent", {}),
        )

@dataclass
class IperfResult(ErrorMixin):
    start: StartInfo = field(default_factory=StartInfo)
    intervals: list[Interval] = field(default_factory=list)
    end: EndInfo = field(default_factory=EndInfo)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            start=StartInfo.from_dict(data.get("start", {})),
            intervals=[Interval.from_dict(i) for i in data.get("intervals", [])],
            end=EndInfo.from_dict(data.get("end", {})),
        )
