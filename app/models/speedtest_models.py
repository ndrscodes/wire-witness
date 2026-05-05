from dataclasses import dataclass
from typing import Any

@dataclass
class PingLatency:
    iqm: float
    low: float
    high: float
    jitter: float

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            iqm=data["iqm"],
            low=data["low"],
            high=data["high"],
            jitter=data["jitter"],
        )


@dataclass
class PingInfo:
    jitter: float
    latency: float
    low: float
    high: float

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            jitter=data["jitter"],
            latency=data["latency"],
            low=data["low"],
            high=data["high"],
        )


@dataclass
class DownloadLatency:
    iqm: float
    low: float
    high: float
    jitter: float

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            iqm=data["iqm"],
            low=data["low"],
            high=data["high"],
            jitter=data["jitter"],
        )


@dataclass
class DownloadInfo:
    bandwidth: int
    bytes: int
    elapsed: int
    latency: DownloadLatency

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            bandwidth=data["bandwidth"],
            bytes=data["bytes"],
            elapsed=data["elapsed"],
            latency=DownloadLatency.from_dict(data["latency"]),
        )


@dataclass
class UploadLatency:
    iqm: float
    low: float
    high: float
    jitter: float

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            iqm=data["iqm"],
            low=data["low"],
            high=data["high"],
            jitter=data["jitter"],
        )


@dataclass
class UploadInfo:
    bandwidth: int
    bytes: int
    elapsed: int
    latency: UploadLatency

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            bandwidth=data["bandwidth"],
            bytes=data["bytes"],
            elapsed=data["elapsed"],
            latency=UploadLatency.from_dict(data["latency"]),
        )


@dataclass
class InterfaceInfo:
    internal_ip: str
    name: str
    mac_addr: str
    is_vpn: bool
    external_ip: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            internal_ip=data["internalIp"],
            name=data["name"],
            mac_addr=data["macAddr"],
            is_vpn=data["isVpn"],
            external_ip=data["externalIp"],
        )


@dataclass
class ServerInfo:
    id: int
    host: str
    port: int
    name: str
    location: str
    country: str
    ip: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            host=data["host"],
            port=data["port"],
            name=data["name"],
            location=data["location"],
            country=data["country"],
            ip=data["ip"],
        )


@dataclass
class ResultInfo:
    id: str
    url: str
    persisted: bool

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            url=data["url"],
            persisted=data["persisted"],
        )


@dataclass
class SpeedtestResult:
    type: str
    timestamp: str
    ping: PingInfo
    download: DownloadInfo
    upload: UploadInfo
    packet_loss: float
    isp: str
    interface: InterfaceInfo
    server: ServerInfo
    result: ResultInfo

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpeedtestResult:
        return cls(
            type=data["type"],
            timestamp=data["timestamp"],
            ping=PingInfo.from_dict(data["ping"]),
            download=DownloadInfo.from_dict(data["download"]),
            upload=UploadInfo.from_dict(data["upload"]),
            packet_loss=float(data["packetLoss"]),
            isp=data["isp"],
            interface=InterfaceInfo.from_dict(data["interface"]),
            server=ServerInfo.from_dict(data["server"]),
            result=ResultInfo.from_dict(data["result"]),
        )
