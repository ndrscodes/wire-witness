import logging
import sys
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BlockingScheduler, BaseScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

import config
import handler
import probers
import influx

logger = logging.getLogger(__name__)

CONFIG_TYPE_MAPPING = {
    config.IPerfConfig: probers.IperfProber,
    config.PingConfig: probers.PingProber,
    config.SpeedtestConfig: probers.SpeedtestProber
}

def create_scheduler(config: config.Config) -> BaseScheduler | None:
    # we do not allow parallel executions as these might influence measurements on other executors.
    executors = {
        "default": ThreadPoolExecutor(max_workers=1)
    }

    if config.influx is None:
        logger.error("InfluxDB configuration is required")
        return None

    influx_client = influx.InfluxClient(config.influx)

    scheduler = BlockingScheduler(executors=executors)

    all_configs = config.ping + config.iperf + config.speedtest

    for cfg in all_configs:
        validation = cfg.validate()
        if not validation.valid:
            logger.error(f"Invalid configuration: {validation.errors}")
            raise Exception(f"Invalid configuration: {cfg} ({validation.errors})")

        if cfg.schedule is None:
            raise Exception("Schedule not defined")
        
        task = handler.TaskHandler(prober=CONFIG_TYPE_MAPPING[type(cfg)](cfg))
        task.subscribe(handler.LogHandler())
        task.subscribe(handler.InfluxHandler(influx_client))
        scheduler.add_job(
            task.execute,
            CronTrigger.from_crontab(cfg.schedule),
            max_instances=1,
            misfire_grace_time=config.grace_time,
            name=cfg.name()
        )

    return scheduler
