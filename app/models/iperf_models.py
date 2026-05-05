from dataclasses import dataclass
from influxdb_client_3 import Point
from typing import Any

@dataclass
class Timestamp:
    time: str
    timesecs: int
    timemillisecs: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            time=data["time"],
            timesecs=data["timesecs"],
            timemillisecs=data["timemillisecs"],
        )


@dataclass
class ConnectionInfo:
    socket: int
    local_host: str
    local_port: int
    remote_host: str
    remote_port: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            socket=data["socket"],
            local_host=data["local_host"],
            local_port=data["local_port"],
            remote_host=data["remote_host"],
            remote_port=data["remote_port"],
        )


@dataclass
class TestStartConfig:
    protocol: str
    num_streams: int
    blksize: int
    omit: int
    duration: int
    bytes: int
    blocks: int
    reverse: int
    tos: int
    target_bitrate: int
    bidir: int
    fqrate: int
    interval: int
    gso: int
    gro: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            protocol=data["protocol"],
            num_streams=data["num_streams"],
            blksize=data["blksize"],
            omit=data["omit"],
            duration=data["duration"],
            bytes=data["bytes"],
            blocks=data["blocks"],
            reverse=data["reverse"],
            tos=data["tos"],
            target_bitrate=data["target_bitrate"],
            bidir=data["bidir"],
            fqrate=data["fqrate"],
            interval=data["interval"],
            gso=data["gso"],
            gro=data["gro"],
        )


@dataclass
class StartInfo:
    connected: list[ConnectionInfo]
    version: str
    system_info: str
    timestamp: Timestamp
    connecting_to: dict
    cookie: str
    tcp_mss_default: int
    target_bitrate: int
    fq_rate: int
    sock_bufsize: int
    snd_buf_actual: int
    rcv_buf_actual: int
    test_start: TestStartConfig

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            connected=[ConnectionInfo.from_dict(c) for c in data["connected"]],
            version=data["version"],
            system_info=data["system_info"],
            timestamp=Timestamp.from_dict(data["timestamp"]),
            connecting_to=data["connecting_to"],
            cookie=data["cookie"],
            tcp_mss_default=data["tcp_mss_default"],
            target_bitrate=data["target_bitrate"],
            fq_rate=data["fq_rate"],
            sock_bufsize=data["sock_bufsize"],
            snd_buf_actual=data["sndbuf_actual"],
            rcv_buf_actual=data["rcvbuf_actual"],
            test_start=TestStartConfig.from_dict(data["test_start"]),
        )


@dataclass
class StreamIntervalData:
    socket: int
    start: float
    end: float
    seconds: float
    bytes: int
    bits_per_second: float
    retransmits: int
    snd_cwnd: int
    snd_wnd: int
    rtt: int
    rttvar: int
    pmtu: int
    reorder: int
    omitted: bool
    sender: bool

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            socket=data["socket"],
            start=data["start"],
            end=data["end"],
            seconds=data["seconds"],
            bytes=data["bytes"],
            bits_per_second=data["bits_per_second"],
            retransmits=data["retransmits"],
            snd_cwnd=data["snd_cwnd"],
            snd_wnd=data["snd_wnd"],
            rtt=data["rtt"],
            rttvar=data["rttvar"],
            pmtu=data["pmtu"],
            reorder=data["reorder"],
            omitted=data["omitted"],
            sender=data["sender"],
        )

@dataclass
class Sum:
    start: float
    end: float
    seconds: float
    bytes: int
    bits_per_second: float
    sender: bool

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            start=data["start"],
            end=data["end"],
            seconds=data["seconds"],
            bytes=data["bytes"],
            bits_per_second=data["bits_per_second"],
            sender=data["sender"],
        )

@dataclass
class SentSum(Sum):
    retransmits: int

    @classmethod
    def from_dict(cls, data):
        return cls(
            start=data["start"],
            end=data["end"],
            seconds=data["seconds"],
            bytes=data["bytes"],
            bits_per_second=data["bits_per_second"],
            sender=data["sender"],
            retransmits=data["retransmits"],
        )

@dataclass
class IntervalSum(Sum):
    omitted: bool

    @classmethod
    def from_dict(cls, data):
        return cls(
            start=data["start"],
            end=data["end"],
            seconds=data["seconds"],
            bytes=data["bytes"],
            bits_per_second=data["bits_per_second"],
            sender=data["sender"],
            omitted=data["omitted"],
        )


@dataclass
class Interval:
    streams: list[StreamIntervalData]
    sum: IntervalSum

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            streams=[StreamIntervalData.from_dict(s) for s in data["streams"]],
            sum=IntervalSum.from_dict(data["sum"]),
        )


@dataclass
class StreamEndSender:
    socket: int
    start: float
    end: float
    seconds: float
    bytes: int
    bits_per_second: float
    retransmits: int
    reorder: int
    max_snd_cwnd: int
    max_snd_wnd: int
    max_rtt: int
    min_rtt: int
    mean_rtt: int
    sender: bool

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            socket=data["socket"],
            start=data["start"],
            end=data["end"],
            seconds=data["seconds"],
            bytes=data["bytes"],
            bits_per_second=data["bits_per_second"],
            retransmits=data["retransmits"],
            reorder=data["reorder"],
            max_snd_cwnd=data["max_snd_cwnd"],
            max_snd_wnd=data["max_snd_wnd"],
            max_rtt=data["max_rtt"],
            min_rtt=data["min_rtt"],
            mean_rtt=data["mean_rtt"],
            sender=data["sender"],
        )


@dataclass
class StreamEndReceiver:
    socket: int
    start: float
    end: float
    seconds: float
    bytes: int
    bits_per_second: float
    sender: bool

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            socket=data["socket"],
            start=data["start"],
            end=data["end"],
            seconds=data["seconds"],
            bytes=data["bytes"],
            bits_per_second=data["bits_per_second"],
            sender=data["sender"],
        )


@dataclass
class StreamEnd:
    sender: StreamEndSender
    receiver: StreamEndReceiver

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            sender=StreamEndSender.from_dict(data["sender"]),
            receiver=StreamEndReceiver.from_dict(data["receiver"]),
        )


@dataclass
class EndInfo:
    streams: list[StreamEnd]
    sum_sent: SentSum
    sum_received: Sum
    cpu_utilization_percent: dict

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            streams=[StreamEnd.from_dict(s) for s in data["streams"]],
            sum_sent=SentSum.from_dict(data["sum_sent"]),
            sum_received=Sum.from_dict(data["sum_received"]),
            cpu_utilization_percent=data["cpu_utilization_percent"],
        )


@dataclass
class IperfResult:
    start: StartInfo
    intervals: list[Interval]
    end: EndInfo

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IperfResult:
        return IperfResult(
            start=StartInfo.from_dict(data["start"]),
            intervals=[Interval.from_dict(i) for i in data["intervals"]],
            end=EndInfo.from_dict(data["end"]),
        )