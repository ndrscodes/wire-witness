from models.speedtest_models import (
    DownloadInfo,
    DownloadLatency,
    UploadInfo,
    UploadLatency,
    PingInfo,
    PingLatency,
    InterfaceInfo,
    ServerInfo,
    ResultInfo,
    SpeedtestResult,
)


def test_download_info_from_dict_with_full_data():
    """Test DownloadInfo.from_dict with complete data including nested latency."""
    data = {
        "bandwidth": 1000000,
        "bytes": 125000000,
        "elapsed": 10000,
        "latency": {
            "iqm": 25.5,
            "low": 10.0,
            "high": 50.0,
            "jitter": 5.0,
        },
    }

    result = DownloadInfo.from_dict(data)

    assert result.bandwidth == 1000000
    assert result.bytes == 125000000
    assert result.elapsed == 10000
    assert isinstance(result.latency, DownloadLatency)
    assert result.latency.iqm == 25.5
    assert result.latency.low == 10.0
    assert result.latency.high == 50.0
    assert result.latency.jitter == 5.0


def test_download_info_from_dict_with_empty_data():
    """Test DownloadInfo.from_dict with empty dict returns defaults."""
    data = {}

    result = DownloadInfo.from_dict(data)

    assert result.bandwidth == 0
    assert result.bytes == 0
    assert result.elapsed == 0
    assert isinstance(result.latency, DownloadLatency)
    assert result.latency.iqm == 0.0
    assert result.latency.low == 0.0
    assert result.latency.high == 0.0
    assert result.latency.jitter == 0.0


def test_download_info_from_dict_with_partial_data():
    """Test DownloadInfo.from_dict with partial data (only some fields)."""
    data = {
        "bandwidth": 500000,
        "latency": {
            "iqm": 15.0,
        },
    }

    result = DownloadInfo.from_dict(data)

    assert result.bandwidth == 500000
    assert result.bytes == 0  # default
    assert result.elapsed == 0  # default
    assert isinstance(result.latency, DownloadLatency)
    assert result.latency.iqm == 15.0
    assert result.latency.low == 0.0  # default
    assert result.latency.high == 0.0  # default
    assert result.latency.jitter == 0.0  # default


def test_download_info_from_dict_with_empty_latency():
    """Test DownloadInfo.from_dict with empty latency object."""
    data = {
        "bandwidth": 750000,
        "bytes": 100000000,
        "elapsed": 5000,
        "latency": {},
    }

    result = DownloadInfo.from_dict(data)

    assert result.bandwidth == 750000
    assert result.bytes == 100000000
    assert result.elapsed == 5000
    assert isinstance(result.latency, DownloadLatency)
    assert result.latency.iqm == 0.0
    assert result.latency.low == 0.0
    assert result.latency.high == 0.0
    assert result.latency.jitter == 0.0


def test_upload_info_from_dict_with_full_data():
    """Test UploadInfo.from_dict with complete data including nested latency."""
    data = {
        "bandwidth": 500000,
        "bytes": 62500000,
        "elapsed": 10000,
        "latency": {
            "iqm": 30.0,
            "low": 15.0,
            "high": 60.0,
            "jitter": 8.0,
        },
    }

    result = UploadInfo.from_dict(data)

    assert result.bandwidth == 500000
    assert result.bytes == 62500000
    assert result.elapsed == 10000
    assert isinstance(result.latency, UploadLatency)
    assert result.latency.iqm == 30.0
    assert result.latency.low == 15.0
    assert result.latency.high == 60.0
    assert result.latency.jitter == 8.0


def test_upload_info_from_dict_with_empty_data():
    """Test UploadInfo.from_dict with empty dict returns defaults."""
    data = {}

    result = UploadInfo.from_dict(data)

    assert result.bandwidth == 0
    assert result.bytes == 0
    assert result.elapsed == 0
    assert isinstance(result.latency, UploadLatency)
    assert result.latency.iqm == 0.0
    assert result.latency.low == 0.0
    assert result.latency.high == 0.0
    assert result.latency.jitter == 0.0


def test_upload_info_from_dict_with_partial_data():
    """Test UploadInfo.from_dict with partial data (only some fields)."""
    data = {
        "bandwidth": 250000,
        "latency": {
            "iqm": 20.0,
        },
    }

    result = UploadInfo.from_dict(data)

    assert result.bandwidth == 250000
    assert result.bytes == 0  # default
    assert result.elapsed == 0  # default
    assert isinstance(result.latency, UploadLatency)
    assert result.latency.iqm == 20.0
    assert result.latency.low == 0.0  # default
    assert result.latency.high == 0.0  # default
    assert result.latency.jitter == 0.0  # default


def test_upload_info_from_dict_with_empty_latency():
    """Test UploadInfo.from_dict with empty latency object."""
    data = {
        "bandwidth": 400000,
        "bytes": 80000000,
        "elapsed": 8000,
        "latency": {},
    }

    result = UploadInfo.from_dict(data)

    assert result.bandwidth == 400000
    assert result.bytes == 80000000
    assert result.elapsed == 8000
    assert isinstance(result.latency, UploadLatency)
    assert result.latency.iqm == 0.0
    assert result.latency.low == 0.0
    assert result.latency.high == 0.0
    assert result.latency.jitter == 0.0


def test_ping_info_from_dict_with_full_data():
    """Test PingInfo.from_dict with complete data."""
    data = {
        "jitter": 2.5,
        "latency": 15.0,
        "low": 10.0,
        "high": 20.0,
    }

    result = PingInfo.from_dict(data)

    assert result.jitter == 2.5
    assert result.latency == 15.0
    assert result.low == 10.0
    assert result.high == 20.0


def test_ping_latency_from_dict_with_full_data():
    """Test PingLatency.from_dict with complete data."""
    data = {
        "iqm": 15.0,
        "low": 10.0,
        "high": 20.0,
        "jitter": 2.5,
    }

    result = PingLatency.from_dict(data)

    assert result.iqm == 15.0
    assert result.low == 10.0
    assert result.high == 20.0
    assert result.jitter == 2.5


def test_interface_info_from_dict_with_full_data():
    """Test InterfaceInfo.from_dict with complete data."""
    data = {
        "internalIp": "192.168.1.100",
        "name": "eth0",
        "macAddr": "00:11:22:33:44:55",
        "isVpn": False,
        "externalIp": "203.0.113.50",
    }

    result = InterfaceInfo.from_dict(data)

    assert result.internal_ip == "192.168.1.100"
    assert result.name == "eth0"
    assert result.mac_addr == "00:11:22:33:44:55"
    assert not result.is_vpn
    assert result.external_ip == "203.0.113.50"


def test_server_info_from_dict_with_full_data():
    """Test ServerInfo.from_dict with complete data."""
    data = {
        "id": 12345,
        "host": "speedtest.example.com",
        "port": 8080,
        "name": "New York - Manhattan",
        "location": "New York, NY",
        "country": "US",
        "ip": "192.0.2.1",
    }

    result = ServerInfo.from_dict(data)

    assert result.id == 12345
    assert result.host == "speedtest.example.com"
    assert result.port == 8080
    assert result.name == "New York - Manhattan"
    assert result.location == "New York, NY"
    assert result.country == "US"
    assert result.ip == "192.0.2.1"


def test_result_info_from_dict_with_full_data():
    """Test ResultInfo.from_dict with complete data."""
    data = {
        "id": "test-123",
        "url": "https://speedtest.example.com/test-123",
        "persisted": True,
    }

    result = ResultInfo.from_dict(data)

    assert result.id == "test-123"
    assert result.url == "https://speedtest.example.com/test-123"
    assert result.persisted


def test_speedtest_result_from_dict_with_full_data():
    """Test SpeedtestResult.from_dict with complete data."""
    data = {
        "type": "speedtest",
        "timestamp": "2024-01-01T12:00:00Z",
        "ping": {
            "jitter": 2.5,
            "latency": 15.0,
            "low": 10.0,
            "high": 20.0,
        },
        "download": {
            "bandwidth": 1000000,
            "bytes": 125000000,
            "elapsed": 10000,
            "latency": {
                "iqm": 25.5,
                "low": 10.0,
                "high": 50.0,
                "jitter": 5.0,
            },
        },
        "upload": {
            "bandwidth": 500000,
            "bytes": 62500000,
            "elapsed": 10000,
            "latency": {
                "iqm": 30.0,
                "low": 15.0,
                "high": 60.0,
                "jitter": 8.0,
            },
        },
        "packetLoss": 0.5,
        "isp": "Example ISP",
        "interface": {
            "internalIp": "192.168.1.100",
            "name": "eth0",
            "macAddr": "00:11:22:33:44:55",
            "isVpn": False,
            "externalIp": "203.0.113.50",
        },
        "server": {
            "id": 12345,
            "host": "speedtest.example.com",
            "port": 8080,
            "name": "New York - Manhattan",
            "location": "New York, NY",
            "country": "US",
            "ip": "192.0.2.1",
        },
        "result": {
            "id": "test-123",
            "url": "https://speedtest.example.com/test-123",
            "persisted": True,
        },
    }

    result = SpeedtestResult.from_dict(data)

    assert result.type == "speedtest"
    assert result.timestamp == "2024-01-01T12:00:00Z"
    assert result.packet_loss == 0.5
    assert result.isp == "Example ISP"
    assert isinstance(result.ping, PingInfo)
    assert result.ping.jitter == 2.5
    assert result.ping.latency == 15.0
    assert isinstance(result.download, DownloadInfo)
    assert result.download.bandwidth == 1000000
    assert isinstance(result.upload, UploadInfo)
    assert result.upload.bandwidth == 500000
    assert isinstance(result.interface, InterfaceInfo)
    assert result.interface.name == "eth0"
    assert isinstance(result.server, ServerInfo)
    assert result.server.id == 12345
    assert isinstance(result.result, ResultInfo)
    assert result.result.id == "test-123"


def test_iperf_result_from_dict():
    pass
