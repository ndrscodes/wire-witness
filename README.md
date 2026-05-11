# WireWitness

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)](https://docs.docker.com/get-started/)
[![GitHub Container](https://img.shields.io/badge/GHCR-Published-blue?style=for-the-badge&logo=github)](https://github.com/ndrscodes/wirewitness/pkgs/container/wirewitness)
[![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![InfluxDB](https://img.shields.io/badge/InfluxDB-3.x-orange?style=for-the-badge&logo=influxdb)](https://www.influxdata.com/)
[![Grafana](https://img.shields.io/badge/Grafana-Ready-purple?style=for-the-badge&logo=grafana)](https://grafana.com/)

> Automated network performance monitoring with InfluxDB & Grafana — track your ISP speeds, internal bandwidth, and network uptime with beautiful dashboards.

WireWitness is an automated network performance monitoring tool. It periodically runs network tests and pushes the results to a time-series database so you can visualize exactly what's happening, and when.

## ⚡ Quick Start

Get WireWitness running end-to-end with InfluxDB and Grafana using Docker Compose.

### Step 1: Clone and Start

```bash
git clone https://github.com/ndrscodes/wirewitness.git
cd wirewitness
```

Create the admin token file required by InfluxDB:

```bash
echo '{"token": "my_admin_token"}' > admin-token.json
```

Start all services:

```bash
docker-compose up -d
```

This single command starts three containers:
- **WireWitness** — runs the monitoring probers
- **InfluxDB 3** — stores all measurement results
- **Grafana** — provides dashboards for visualization

### Step 2: Access Grafana

Open your browser and navigate to:

```
http://localhost:3000
```

Log in with the default Grafana credentials (username: `admin`, password: `admin`). Grafana is pre-configured with the InfluxDB datasource.

### Step 3: View Your Metrics

After a short wait (the first cron jobs need to fire), you'll see network metrics flowing in:

| Prober | What It Measures |
|--------|-----------------|
| **Ping** | Latency and packet loss to target hosts |
| **iPerf3** | Internal network bandwidth and throughput |
| **Speedtest** | ISP download/upload speeds and latency |

> **Note:** The default cron schedules run every minute for testing. See [Configuration](#configuration--options) to customize frequencies.

### Stopping WireWitness

```bash
docker-compose down
```

---

## Prerequisites

### For Docker Setup (Recommended)

| Requirement | Details |
|-------------|---------|
| **Docker** | Installed and running ([install guide](https://docs.docker.com/get-docker/)) |
| **Docker Compose** | Included with Docker Desktop or install separately ([install guide](https://docs.docker.com/compose/install/)) |
| **Disk Space** | ~2 GB minimum (InfluxDB + Grafana + WireWitness images) |
| **RAM** | ~1 GB minimum |
| **Network** | Ports `3000` (Grafana) and `8181` (InfluxDB) must be available |

This is the recommended approach for beginners. Docker Compose bundles WireWitness, InfluxDB, and Grafana into a single command.

### For Bare-Metal / Local Setup

If you prefer to run WireWitness on your host machine (e.g., Raspberry Pi, home server, or development machine):

| Requirement | Details |
|-------------|---------|
| **Python** | Version 3.8 or higher |
| **System Tools** | `ping`, `iperf3`, and the official Ookla `speedtest` CLI must be installed and on your `$PATH` |
| **InfluxDB** | An InfluxDB v3 instance must be running (local or remote) |
| **pip** | Python package manager for installing dependencies |

> **Note:** The Docker image already includes `iperf3` and the official Ookla `speedtest` CLI. For bare-metal setups, you need to install these yourself. See [`install-speedtest.sh`](install-speedtest.sh) for the official Ookla Speedtest CLI installation script.

### External Dependencies

WireWitness requires the following external services:

| Service | Purpose | Required? |
|---------|---------|-----------|
| **InfluxDB v3** | Time-series database for storing metrics | **Yes** |
| **Grafana** | Visualization and dashboards (optional but recommended) | No |
| **iperf3** | Bandwidth testing tool | Only for iPerf prober |
| **Ookla Speedtest CLI** | ISP speed testing | Only for Speedtest prober |

You can run WireWitness with just InfluxDB and use any visualization tool you prefer instead of Grafana.

## Why WireWitness?

WireWitness solves the problem of "blind spots" in your network monitoring by doing the heavy lifting for you.

Most network monitoring tools are either too complex (full enterprise APM suites) or too limited (simple uptime pingers). WireWitness fills the gap by providing **focused, automated network performance testing** that runs in the background and builds a historical record you can actually use.

### Key Benefits

- **Hold your ISP accountable** — Build historical evidence of speed drops, outages, and performance issues
- **Monitor your entire network** — From ISP connections to internal LAN bandwidth, all in one place
- **Lightweight and portable** — Run it on a Raspberry Pi, a home server, or in the cloud. Deploy at remote sites with a single command
- **Flexible scheduling** — Run tests as frequently as you want, on your own schedule, targeting any host

Note that `speedtest` mentioned here is the official Ookla Speedtest CLI, not the community `speedtest-cli` tool. Both tools behave differently and create different output, so be sure to use the official Ookla tool if setting up locally. The docker image already uses the correct tool.

## Use Cases

WireWitness is designed for a variety of network monitoring scenarios. Here are some common use cases:

### 📡 Monitor ISP Performance

Track your internet download/upload speeds and latency over time to identify patterns and hold your ISP accountable.

- **Detect speed drops** — Get alerted when your actual speeds fall below your subscribed plan
- **Find patterns** — Discover if your connection degrades at certain times of day
- **Build evidence** — Export historical data to support complaints or service disputes
- **Compare promises vs reality** — See if your "up to X Mbps" plan delivers consistent performance

### 🏠 Monitor Internal Network

Measure bandwidth and latency between devices on your local network using `iperf3`.

- **Identify bottlenecks** — Find which links are saturated or underperforming
- **WiFi vs Ethernet** — Compare wireless and wired performance over time
- **Monitor critical services** — Track latency to NAS, servers, and other infrastructure
- **Validate upgrades** — Verify that new switches, routers, or cabling actually improve performance

### 🟢 Monitor Uptime & Availability

Ping critical services to detect outages and track availability over time.

- **Service monitoring** — Track availability of DNS servers, gateways, and external services
- **Intermittent issues** — Catch packet loss or latency spikes that happen randomly
- **Multi-target monitoring** — Monitor multiple hosts simultaneously (Google DNS, Cloudflare, your router, etc.)
- **Historical trends** — See if a "flaky" connection is getting worse over time

### 🌍 Multi-Site Monitoring

Deploy WireWitness at remote locations and have them all report to a central InfluxDB instance.

- **Branch office monitoring** — Track network quality across multiple locations
- **Edge site visibility** — Monitor connectivity at sites you don't have physical access to
- **Centralized dashboards** — View all locations in a single Grafana dashboard

### 💡 What Metrics Will You Collect?

| Prober | Metrics Collected |
|--------|------------------|
| **Ping** | Latency (min/avg/max), jitter, packet loss, round-trip times |
| **iPerf3** | Download/upload throughput, jitter, packet loss, TCP/UDP stats |
| **Speedtest** | Download/upload speed, latency, jitter, server info, ISP data |

---

## How It Works

WireWitness follows a simple three-stage pipeline: **measure → store → visualize**.

### Stage 1: Measure (WireWitness Probers)

WireWitness runs three types of network probers, each measuring different aspects of your network:

| Prober | Tool Used | What It Measures |
|--------|-----------|-----------------|
| **Ping** | System `ping` | Latency, jitter, packet loss to target hosts |
| **iPerf3** | `iperf3` CLI | Internal network bandwidth, throughput, TCP/UDP stats |
| **Speedtest** | Ookla `speedtest` CLI | ISP download/upload speeds, latency |

Each prober runs on a configurable schedule (using cron syntax). You can enable any combination of probers and configure multiple tasks per prober type (e.g., ping multiple different hosts).

### Stage 2: Store (InfluxDB)

After each test completes, WireWitness writes the results to an InfluxDB v3 time-series database. Every measurement is timestamped and tagged with metadata (target host, prober type, etc.).

### Stage 3: Visualize (Grafana)

Grafana connects to InfluxDB and provides beautiful dashboards to visualize your network metrics. WireWitness ships with a Docker Compose setup that includes Grafana pre-configured with the InfluxDB datasource.

### Scheduling

WireWitness uses cron-based scheduling for each prober. This means:

- Each prober can run on its own schedule
- You can have multiple tasks per prober type (e.g., ping 3 different hosts)
- Schedules are configured via YAML, environment variables, or CLI arguments
- Missed jobs can be recovered using the `grace_time` setting

---

## Getting Started: How to Run WireWitness

### Option 1: Docker
Docker compose is the absolute fastest way to get everything running, as it spins up WireWitness, an InfluxDB v3 instance, and Grafana all at once.
The docker image in this repository comes with the `speedtest` CLI and `iperf3` already installed, so you don't have to worry about that.

```bash
docker-compose up -d
```

You can, of course, also run only the WireWitness container and let it send measurements to a remote InfluxDB instance. A pre-built Docker image is published to GitHub Container Registry (GHCR) on every release.

```bash
# Pull the latest released image from GHCR
docker pull ghcr.io/ndrscodes/wirewitness:latest

# Run the pulled image
docker run -d ghcr.io/ndrscodes/wirewitness:latest
```

Alternatively, you can build the image locally:

```bash
docker build -t wirewitness:latest .
docker run -d wirewitness:latest
```

See below for more details on how to configure WireWitness.

### Option 2: The Bare-Metal / Local Way
The tool can also be run locally on a Raspberry Pi or any other machine.

1. Ensure you have Python 3 installed on your system.
2. Install the necessary Python packages (`pip install -r requirements.txt`).
3. Make sure `iperf3` and the `speedtest` CLI are installed and accessible on your machine. You can also omit running either tool by not configuring a schedule. Unconfigured tools will be skipped silently.
4. Run the application:

```bash
python main.py
```

Hint: You can always run `python main.py --dry-run` to validate your configuration and ensure everything looks good without actually starting the scheduler.

## Configuration & Options

WireWitness is highly customizable to fit your needs. You can configure it using three different methods:

1. **YAML Configuration Files** - Most flexible, supports all features including multiple tasks
2. **Environment Variables** - Useful for Docker and containerized deployments
3. **Command-Line Arguments** - Quick overrides and testing

If you provide multiple configuration sources, they are merged with the following precedence (highest to lowest):
- Command-Line Arguments (highest priority)
- Environment Variables
- YAML Configuration File (lowest priority)

This means CLI arguments override environment variables, which override YAML file settings.

### Configuration via YAML File

The most flexible way to configure WireWitness is using a YAML configuration file. This method supports all features including multiple tasks per prober type.

**Basic Usage:**

```bash
python main.py --config-file config.yaml
```

Or set the environment variable:

```bash
export WIREWITNESS_CONFIG_FILE=config.yaml
python main.py
```

**Example YAML Structure:**

```yaml
influx:
  host: "http://influx:8086"
  org: "wirewitness"
  database: "wirewitness"
  token: "your-token-here"
  # OR use token_file for Docker secrets:
  # token_file: "/run/secrets/influx-admin-token"

ping:
  tasks:
    - schedule: "*/5 * * * *"
      target_host: "8.8.8.8"
      count: 5
    - schedule: "*/5 * * * *"
      target_host: "1.1.1.1"
      count: 5

iperf:
  tasks:
    - schedule: "0 * * * *"
      target_host: "192.168.1.100"
      duration: 10

speedtest:
  accept_gdpr: true
  accept_license: true
  tasks:
    - schedule: "0 0 * * *"
      additional_flags: ""

grace_time: 30
```

See [`config.example.yaml`](config.example.yaml) for a comprehensive example with detailed comments.

**Key Features:**
- Support for **multiple tasks** per prober type (ping, iperf, speedtest)
- All configuration options available
- Token can be loaded from a file (useful for Docker secrets) or specified directly
- Optional `grace_time` for cron job scheduling flexibility

### Configuration via Environment Variables

You can configure WireWitness entirely through environment variables, which is useful for Docker deployments.

```bash
export INFLUXDB_HOST=http://influx:8086
export INFLUXDB_ORG=wirewitness
export INFLUXDB_DATABASE=wirewitness
export INFLUXDB_TOKEN=your-token-here
export PING_TARGET_HOST=8.8.8.8
export PING_CRON_SCHEDULE="*/5 * * * *"
python main.py
```

### Configuration via CLI Arguments

You can override configuration using command-line arguments:

```bash
python main.py \
  --influx-host http://influx:8086 \
  --influx-org wirewitness \
  --ping-host 8.8.8.8 \
  --ping-schedule "*/5 * * * *"
```

**Note:** CLI arguments only support a single task per prober type. For multiple tasks, use YAML configuration.

### Configuration Precedence

When multiple configuration sources are provided, they are merged with this precedence:

```
CLI Arguments > Environment Variables > YAML File
```

**Example:** If you have a YAML file with `PING_TARGET_HOST=8.8.8.8` and also set `--ping-host 1.1.1.1` on the command line, the CLI argument wins and ping will target `1.1.1.1`.

### Database (InfluxDB) Settings

| Configuration | Environment Variable | Command-Line Argument | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| **Host URL** | `INFLUXDB_HOST` | `--influx-host` | The URL where your InfluxDB instance lives. | *Required* |
| **Organization** | `INFLUXDB_ORG` | `--influx-org` | Your InfluxDB organization name. | *Required* |
| **Database** | `INFLUXDB_DATABASE` | `--influx-database` | The target bucket or database for your network metrics. | `wirewitness` |
| **Auth Token** | `INFLUXDB_TOKEN` | `--influx-token` | Your secret authentication token. | *None* |
| **Token File** | `INFLUXDB_TOKEN_FILE` | `--influx-token-file` | Path to a file containing your auth token (JSON format with "token" key). | `/run/secrets/influx-admin-token` |
| **Max Retry** | `MAX_RETRY_TIME` | `--max-retry-time` | How long (in milliseconds) to keep trying if the database is temporarily unreachable. | `86400000` (24 hours) |
| **Max Delay** | `MAX_RETRY_DELAY` | `--max-retry-delay` | How long (in milliseconds) to wait before retrying if the database is temporarily unreachable. | `120000` (2 minutes) |
| **Retry Interval** | `RETRY_INTERVAL` | `--retry-interval` | How often (in milliseconds) to retry if the database is temporarily unreachable. | `5000` (5 seconds) |

**Token File Format:**

The token file must be a JSON file with a "token" key:

```json
{
  "token": "your-influxdb-admin-token-here"
}
```

This format is compatible with Docker secrets, making it easy to use in containerized deployments.

### iperf3 Settings

| Configuration | Environment Variable | Command-Line Argument | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| **Target Host** | `IPERF_TARGET_HOST` | `--iperf-host` | The IP address or hostname of your destination iperf3 server. | *None* |
| **Schedule** | `IPERF_CRON_SCHEDULE` | `--iperf-schedule` | When to run the test (uses standard cron syntax, e.g., `*/5 * * * *`). | *None* |
| **Duration** | `IPERF_DURATION` | `--iperf-duration` | How many seconds the speed test should blast traffic across your network. | `10` |
| **Command Path**| `IPERF_CMD` | `--iperf-cmd` | The path to your local iperf3 binary. | Uses the installed `iperf3` binary |
| **Extra Flags** | `IPERF_ADDITIONAL_FLAGS` | *N/A* | Pass extra flags to iperf3. | *None* |

**Multiple Tasks:** YAML configuration supports multiple iperf3 tasks to different hosts. CLI arguments only support a single task.

### ping Settings

| Configuration | Environment Variable | Command-Line Argument | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| **Target Host** | `PING_TARGET_HOST` | `--ping-host` | The IP address or hostname you want to ping. | *None* |
| **Schedule** | `PING_CRON_SCHEDULE` | `--ping-schedule` | When to run the test (cron syntax). | *None* |
| **Count** | `PING_COUNT` | `--ping-count` | How many ping packets to send each time. | `5` |
| **Command Path**| `PING_CMD` | `--ping-cmd` | The path to your local ping binary. | Uses the installed `ping` binary |

**Multiple Tasks:** YAML configuration supports multiple ping tasks to different hosts. CLI arguments only support a single task.

### Speedtest Settings

| Configuration | Environment Variable | Command-Line Argument | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| **Schedule** | `SPEEDTEST_CRON_SCHEDULE` | `--speedtest-schedule` | When to run the internet speed test (standard cron syntax). | *None* |
| **Accept GDPR** | `SPEEDTEST_GDPR_ACCEPT` | `--accept-speedtest-gdpr` *no value required* | You must accept Ookla's GDPR terms to run the prober. | `False` |
| **Accept License**| `SPEEDTEST_LICENSE_ACCEPT`| `--accept-speedtest-license` *no value required* | You must accept Ookla's License terms to run the prober. | `False` |
| **Command Path**| `SPEEDTEST_CMD` | `--speedtest-cmd` | The path to your Ookla speedtest binary. | Uses the installed `speedtest` binary. |
| **Extra Flags** | `SPEEDTEST_ADDITIONAL_FLAGS`| *N/A* | Target specific servers or interfaces by passing extra flags here (see `speedtest --help`). | *None* |

**Important:** Both GDPR and License acceptance are **REQUIRED** for speedtest to run. Without both flags set to `true`, the speedtest prober will fail validation and not execute.

### Utility Options
A few extra knobs and dials to help you manage the application.

| Configuration | Environment Variable | Command-Line Argument | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| **Config File** | `WIREWITNESS_CONFIG_FILE` | `--config-file` | Path to YAML configuration file. Enables the most flexible configuration method. | *None* |
| **Grace Time** | `MISFIRE_GRACE_TIME` | `--misfire-grace-time` | Grace period (in seconds) for cron jobs that missed their exact start time. | *None* (allows indefinite delay of tasks, meaning they will be started even if their scheduled time has passed) |
| **Log Level** | *N/A* | `--log-level` | How chatty the application should be (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | `INFO` |
| **Dry Run** | *N/A* | `--dry-run` | Validates your config and exits peacefully without starting the scheduler. | `False` |

## Troubleshooting

### Container won't start

```bash
# Check container logs
docker logs wire_witness
```

Common causes:
- **InfluxDB not ready** — WireWitness starts before InfluxDB is ready. Wait a moment and restart: `docker-compose restart wire_witness`
- **Token file missing** — Ensure `admin-token.json` exists with valid JSON: `{"token": "your-token"}`
- **Port already in use** — Port `3000` (Grafana) or `8181` (InfluxDB) may be in use. Change the port mapping in `docker-compose.yml`

### No data appearing in Grafana

1. **Check WireWitness logs** — Look for errors writing to InfluxDB: `docker logs wire_witness`
2. **Verify InfluxDB is running** — `docker ps | grep influx`
3. **Check the token** — Ensure the token in `admin-token.json` matches the one InfluxDB was started with
4. **Verify cron schedules** — If all schedules are `* None * * * *`, no tests will run. Set at least one schedule

### High latency or failed tests

- **Target host unreachable** — Verify the target host is reachable from the WireWitness container: `docker exec -it wire_witness ping 8.8.8.8`
- **Speedtest fails** — Ensure you've set `SPEEDTEST_GDPR_ACCEPT=yes` and `SPEEDTEST_LICENSE_ACCEPT=yes`
- **iperf3 connection refused** — Ensure an iperf3 server is running on the target host: `iperf3 -s` on the server side

### "Config validation failed" errors

- **Speedtest** — Both `accept_gdpr` and `accept_license` must be truthy
- **Missing required fields** — Each prober type needs at least a `target_host` and a `schedule`
- **Invalid cron expression** — Use a [cron validator](https://crontab.guru/) to check your schedule syntax

### Getting more debug info

Run WireWitness in debug mode for verbose output:

```bash
# Docker
docker-compose up --detach && docker logs -f wire_witness

# Bare-metal
python main.py --log-level DEBUG
```

Use `--dry-run` to validate your configuration without starting the scheduler:

```bash
python main.py --config-file config.yaml --dry-run
```

## Contributing

I appreciate your interest in helping improve this tool. 
WireWitness is built on the spirit of open source and community collaboration.

If you encounter any bugs or have ideas for new features, please feel free to open an issue or submit a pull request. 
The goal is simply to provide a helpful resource for anyone trying to better understand their network.

## Planned Features

The following features are planned for future releases:

* Local SQL storage for metrics
* Optional Prometheus integration
* Custom local dashboard for displaying the most relevant metrics

Community contributions are welcome! If you're interested in helping implement any of these features, please open an issue or pull request.
