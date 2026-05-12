from models.iperf_models import Timestamp, ConnectionInfo, TestStartConfig, StartInfo, StreamIntervalData, IntervalSum, SentSum, StreamEndSender, StreamEndReceiver, IperfResult, EndInfo, Interval, StreamEnd


def test_timestamp_from_dict():
    """Test Timestamp.from_dict with complete data."""
    data = {
        "time": "2024-01-01T12:00:00Z",
        "timesecs": 1704110400,
        "timemillisecs": 1704110400000,
    }

    result = Timestamp.from_dict(data)

    assert result.time == "2024-01-01T12:00:00Z"
    assert result.timesecs == 1704110400
    assert result.timemillisecs == 1704110400000


def test_connection_info_from_dict():
    """Test ConnectionInfo.from_dict with complete data."""
    data = {
        "socket": 42,
        "local_host": "192.168.1.10",
        "local_port": 52013,
        "remote_host": "10.0.0.1",
        "remote_port": 5201,
    }

    result = ConnectionInfo.from_dict(data)

    assert result.socket == 42
    assert result.local_host == "192.168.1.10"
    assert result.local_port == 52013
    assert result.remote_host == "10.0.0.1"
    assert result.remote_port == 5201


def test_test_start_config_from_dict():
    """Test TestStartConfig.from_dict with complete data — all non-default values."""
    data = {
        "protocol": "UDP",
        "num_streams": 4,
        "blksize": 8192,
        "omit": 5,
        "duration": 30,
        "bytes": 1048576,
        "blocks": 1000,
        "reverse": 1,
        "tos": 161,
        "target_bitrate": 1000000,
        "bidir": 1,
        "fqrate": 500000,
        "interval": 2,
        "gso": 1,
        "gro": 1,
    }

    result = TestStartConfig.from_dict(data)

    assert result.protocol == "UDP"
    assert result.num_streams == 4
    assert result.blksize == 8192
    assert result.omit == 5
    assert result.duration == 30
    assert result.bytes == 1048576
    assert result.blocks == 1000
    assert result.reverse == 1
    assert result.tos == 161
    assert result.target_bitrate == 1000000
    assert result.bidir == 1
    assert result.fqrate == 500000
    assert result.interval == 2
    assert result.gso == 1
    assert result.gro == 1


def test_start_info_from_dict():
    """Test StartInfo.from_dict — asserts StartInfo-level fields only; nested objects are tested individually."""
    data = {
        "version": "3.17",
        "system_info": "Linux host 5.15.0 x86_64",
        "cookie": "ABC123XYZ",
        "tcp_mss_default": 1460,
        "target_bitrate": 0,
        "fq_rate": 0,
        "sock_bufsize": 0,
        "sndbuf_actual": 262144,
        "rcvbuf_actual": 262144,
    }

    result = StartInfo.from_dict(data)

    assert len(result.connected) == 0
    assert result.version == "3.17"
    assert result.system_info == "Linux host 5.15.0 x86_64"
    assert result.cookie == "ABC123XYZ"
    assert result.tcp_mss_default == 1460
    assert result.snd_buf_actual == 262144
    assert result.rcv_buf_actual == 262144


def test_stream_interval_data_from_dict():
    """Test StreamIntervalData.from_dict — asserts StreamIntervalData-level fields only."""
    data = {
        "socket": 5,
        "start": 0.0,
        "end": 10.005,
        "seconds": 10.005,
        "bytes": 1250000000,
        "bits_per_second": 1000000000.0,
        "retransmits": 3,
        "snd_cwnd": 256,
        "snd_wnd": 32768,
        "rtt": 15,
        "rttvar": 5,
        "pmtu": 1460,
        "reorder": 0,
        "omitted": False,
        "sender": True,
    }

    result = StreamIntervalData.from_dict(data)

    assert result.socket == 5
    assert result.start == 0.0
    assert result.end == 10.005
    assert result.seconds == 10.005
    assert result.bytes == 1250000000
    assert result.bits_per_second == 1000000000.0
    assert result.retransmits == 3
    assert result.snd_cwnd == 256
    assert result.snd_wnd == 32768
    assert result.rtt == 15
    assert result.rttvar == 5
    assert result.pmtu == 1460
    assert result.reorder == 0
    assert result.omitted is False


def test_sent_sum_from_dict():
    """Test SentSum.from_dict — asserts SentSum-level fields (inherited Sum fields + retransmits)."""
    data = {
        "start": 0.0,
        "end": 20.01,
        "seconds": 20.01,
        "bytes": 5000000000,
        "bits_per_second": 2000000000.0,
        "sender": True,
        "retransmits": 12,
    }

    result = SentSum.from_dict(data)

    assert result.start == 0.0
    assert result.end == 20.01
    assert result.seconds == 20.01
    assert result.bytes == 5000000000
    assert result.bits_per_second == 2000000000.0
    assert result.sender is True
    assert result.retransmits == 12


def test_interval_sum_from_dict():
    """Test IntervalSum.from_dict — asserts IntervalSum-level fields (inherited Sum fields + omitted)."""
    data = {
        "start": 0.0,
        "end": 10.005,
        "seconds": 10.005,
        "bytes": 2500000000,
        "bits_per_second": 2000000000.0,
        "sender": True,
        "omitted": False,
    }

    result = IntervalSum.from_dict(data)

    assert result.start == 0.0
    assert result.end == 10.005
    assert result.seconds == 10.005
    assert result.bytes == 2500000000
    assert result.bits_per_second == 2000000000.0
    assert result.sender is True
    assert result.omitted is False


def test_stream_end_sender_from_dict():
    """Test StreamEndSender.from_dict — asserts StreamEndSender-level fields only."""
    data = {
        "socket": 3,
        "start": 0.0,
        "end": 20.01,
        "seconds": 20.01,
        "bytes": 5000000000,
        "bits_per_second": 2000000000.0,
        "retransmits": 8,
        "reorder": 2,
        "max_snd_cwnd": 512,
        "max_snd_wnd": 65536,
        "max_rtt": 25,
        "min_rtt": 10,
        "mean_rtt": 15,
        "sender": True,
    }

    result = StreamEndSender.from_dict(data)

    assert result.socket == 3
    assert result.start == 0.0
    assert result.end == 20.01
    assert result.seconds == 20.01
    assert result.bytes == 5000000000
    assert result.bits_per_second == 2000000000.0
    assert result.retransmits == 8
    assert result.reorder == 2
    assert result.max_snd_cwnd == 512
    assert result.max_snd_wnd == 65536
    assert result.max_rtt == 25
    assert result.min_rtt == 10
    assert result.mean_rtt == 15
    assert result.sender is True


def test_stream_end_receiver_from_dict():
    """Test StreamEndReceiver.from_dict — asserts StreamEndReceiver-level fields only."""
    data = {
        "socket": 3,
        "start": 0.0,
        "end": 20.01,
        "seconds": 20.01,
        "bytes": 4500000000,
        "bits_per_second": 1800000000.0,
        "sender": False,
    }

    result = StreamEndReceiver.from_dict(data)

    assert result.socket == 3
    assert result.start == 0.0
    assert result.end == 20.01
    assert result.seconds == 20.01
    assert result.bytes == 4500000000
    assert result.bits_per_second == 1800000000.0
    assert result.sender is False


def test_iperf_result_from_dict():
    """Test IperfResult.from_dict — top-level integration. Minimal data per nested object; single property check to confirm correct field assignment."""
    data = {
        "start": {"version": "3.17"},
        "intervals": [
            {
                "streams": [{"socket": 3}],
                "sum": {"bytes": 250000000},
            },
        ],
        "end": {
            "streams": [
                {
                    "sender": {"socket": 3},
                    "receiver": {"socket": 3},
                },
            ],
            "sum_sent": {"bytes": 5000000000},
            "sum_received": {"bytes": 4500000000},
            "cpu_utilization_percent": {"user": 45.2},
        },
    }

    result = IperfResult.from_dict(data)

    assert result.start.version == "3.17"
    assert result.end.sum_sent.bytes == 5000000000
    assert result.end.cpu_utilization_percent == {"user": 45.2}
    assert len(result.intervals) == 1
    assert result.intervals[0].sum.bytes == 250000000
    assert result.intervals[0].streams[0].socket == 3
    assert result.end.streams[0].sender.socket == 3
    assert result.end.streams[0].receiver.socket == 3
