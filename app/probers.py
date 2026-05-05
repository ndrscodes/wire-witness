import json
import logging
import os
import re
from dataclasses import dataclass
from subprocess import PIPE, run
from shutil import which
from typing import Any

from config import Config
from models.speedtest_models import SpeedtestResult
from models.iperf_models import IperfResult
from models.ping_models import PingResult

logger = logging.getLogger(__name__)

def _parse_and_validate_flags(flag_string: str, allowed_flags: set[str], tool_name: str) -> list[str]:
    if not flag_string.strip():
        return []
    
    entries = [e.strip() for e in flag_string.split(",") if e.strip()]
    validated = []
    
    for entry in entries:
        parts = entry.split()
        flag_name = parts[0]
        
        if flag_name not in allowed_flags:
            logger.warning("Skipping disallowed %s flag: %s", tool_name, flag_name)
            continue
        
        validated.extend(parts)
    
    return validated


class ProberInterface:
    def probe(self) -> SpeedtestResult | IperfResult | dict[str, Any] | PingResult:
        raise NotImplementedError

    def ready(self) -> bool:
        return False

class SpeedtestProber(ProberInterface):
    PROG_NAME: str | None = Config.SPEEDTEST_CMD
    
    SPEEDTEST_ALLOWED_FLAGS = {
        # Server selection
        "-s", "--server-id",
        "-I", "--interface",
        "-i", "--ip",
        "-o", "--host",
        # Progress and display
        "-p", "--progress",
        "-P", "--precision",
        "-f", "--format",
        "--progress-update-interval",
        "-u", "--unit",
        "-a", "-A", "-b", "-B",
        "--selection-details",
        "--ca-certificate",
        "-v",
        "--output-header",
    }
    
    @classmethod
    def __get_cli_opts(cls) -> list[str]:
        opts = ["--format=json"]
        if Config.ACCEPT_SPEEDTEST_GDPR:
            opts.append("--accept-gdpr")
        if Config.ACCEPT_SPEEDTEST_LICENSE:
            opts.append("--accept-license")
        
        additional = _parse_and_validate_flags(
            Config.SPEEDTEST_ADDITIONAL_FLAGS, cls.SPEEDTEST_ALLOWED_FLAGS, "speedtest"
        )
        opts.extend(additional)
        
        return opts

    def __run(self):
        if self.PROG_NAME is None:
            raise Exception("Speedtest command not configured")
        
        logger.info("Starting speedtest")
        proc = run([self.PROG_NAME] + self.__get_cli_opts(), stdout=PIPE, stderr=PIPE)
        if proc.returncode == 0:
            return proc.stdout
        
        raise Exception(f"process returned error (return code {proc.returncode}, {proc.stderr})")

    def probe(self) -> SpeedtestResult:
        stdout = self.__run()
        data = json.loads(stdout)
        return SpeedtestResult.from_dict(data)

    def ready(self) -> bool:
        if not Config.ACCEPT_SPEEDTEST_LICENSE or not Config.ACCEPT_SPEEDTEST_GDPR:
            logger.warning("Speedtest license and/or GDPR not accepted. Not ready.")
            return False
        return self.PROG_NAME is not None


class IperfProber(ProberInterface):
    PROG_NAME = Config.IPERF_CMD
    TARGET_HOST = Config.IPERF_TARGET_HOST
    DURATION = Config.IPERF_DURATION
    
    IPERF_ALLOWED_FLAGS = {
        # Common flags
        "-p", "--port",
        "-f", "--format",
        "-i", "--interval",
        "-I", "--pidfile",
        "-F", "--file",
        "-B", "--bind",
        "--bind-dev",
        "-V", "--verbose",
        "--logfile",
        "--forceflush",
        "--timestamps",
        "--rcv-timeout",
        # Client-specific flags
        "-u", "--udp",
        "--connect-timeout",
        "-b", "--bitrate",
        "--pacing-timer",
        "-n", "--bytes",
        "-k", "--blockcount",
        "-l", "--length",
        "--cport",
        "-P", "--parallel",
        "-R", "--reverse",
        "--bidir",
        "-w", "--window",
        "-M", "--set-mss",
        "-N", "--no-delay",
        "-4", "--version4",
        "-6", "--version6",
        "-S", "--tos",
        "--dscp",
        "-Z", "--zerocopy",
        "--skip-rx-copy",
        "-O", "--omit",
        "-T", "--title",
        "--extra-data",
        "--udp-counters-64bit",
        "--gsro",
        "--repeating-payload",
        "--dont-fragment",
    }

    def __run(self, host: str | None = None):
        host = host or self.TARGET_HOST
        logger.info("Starting iperf (host=%s, duration=%ds)", host, self.DURATION)
        
        base_cmd = [self.PROG_NAME, "-c", host, "-t", str(self.DURATION), "--json"]
        
        additional = _parse_and_validate_flags(
            Config.IPERF_ADDITIONAL_FLAGS, self.IPERF_ALLOWED_FLAGS, "iperf3"
        )
        
        proc = run(
            base_cmd + additional,
            stdout=PIPE,
            stderr=PIPE,
        )
        if proc.returncode == 0:
            return proc.stdout

        # iperf uses stdout instead of stderr for errors
        raise Exception(f'iperf3 process returned error: {json.loads(proc.stdout.decode())["error"]}')

    def probe(self, host: str | None = None) -> IperfResult:
        stdout = self.__run(host)
        data = json.loads(stdout)
        return IperfResult.from_dict(data)

    def ready(self) -> bool:
        return bool(self.PROG_NAME and self.TARGET_HOST)

class PingProber(ProberInterface):
    COUNT = Config.PING_COUNT
    HOST = Config.PING_TARGET_HOST
    OPTS = [Config.PING_CMD, "-c", str(COUNT), "-q", HOST]
    PACKET_LOSS_REGEX = re.compile(r"(\d+(?:\.\d+)?)% packet loss")
    LATENCY_REGEX = re.compile(r"round-trip min/avg/max(?:stddev)? = (\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?) ms")
    HOST_IP_REGEX = re.compile(r"PING (\S+) \((\S+)\)")

    def __run(self):
        proc = run(self.OPTS, stdout=PIPE, stderr=PIPE)
        if proc.returncode == 0:
            return proc.stdout
        raise Exception(f"ping process returned error (return code {proc.returncode}, {proc.stderr})")
    
    def __parse_output(self, output: bytes) -> PingResult:
        lines = output.decode().splitlines()

        if len(lines) < 3:
            raise Exception(f"unexpected ping output: {output}")
        
        host_line = lines[0]
        packet_line = lines[-2]
        stats_line = lines[-1]
        
        host_ip_match = self.HOST_IP_REGEX.search(host_line)
        packet_loss_match = self.PACKET_LOSS_REGEX.search(packet_line)
        latency_match = self.LATENCY_REGEX.search(stats_line)
        if not packet_loss_match or not latency_match or not host_ip_match:
            raise Exception(f"unexpected ping output: {output}")
        
        return PingResult(
            packet_loss=float(packet_loss_match.group(1)),
            min_latency=float(latency_match.group(1)),
            avg_latency=float(latency_match.group(2)),
            max_latency=float(latency_match.group(3)),
            host=host_ip_match.group(1),
            ip=host_ip_match.group(2),
        )

    def probe(self) -> PingResult:
        output = self.__run()
        return self.__parse_output(output)
    
    def ready(self) -> bool:
        if Config.PING_CMD is not None and Config.PING_TARGET_HOST is not None and Config.PING_COUNT > 0:
            return True
        logger.warning("Ping command, target host or count not properly configured. Not ready.")
        return False