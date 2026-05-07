import logging
import sys
from apscheduler.triggers.cron import CronTrigger, BaseTrigger
from apscheduler.schedulers.background import BlockingScheduler, BaseScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from dataclasses import dataclass

import config
import handler
import probers
import influx

logger = logging.getLogger(__name__)

@dataclass
class Task:
    trigger: BaseTrigger
    handler: handler.TaskHandler
    name: str

def iperf_to_prober(config: config.IPerfConfig, task_config: config.IPerfTask) -> probers.IperfProber:
    return probers.IperfProber(task_config, config.cmd)

def ping_to_prober(config: config.PingConfig, task_config: config.PingTask) -> probers.PingProber:
    return probers.PingProber(task_config, config.cmd)

def speedtest_to_prober(config: config.SpeedtestConfig, task_config: config.SpeedtestTask) -> probers.SpeedtestProber:
    print(f"speedtest to prober {config} {task_config}")
    return probers.SpeedtestProber(task_config, config.cmd, config.accept_gdpr, config.accept_license)

CONFIG_GENERATOR_MAPPING = {
    config.IPerfConfig: iperf_to_prober,
    config.PingConfig: ping_to_prober,
    config.SpeedtestConfig: speedtest_to_prober
}

def to_jobs(config: config.SpeedtestConfig | config.IPerfConfig | config.PingConfig, common_subscribers: list[handler.SubscriberInterface]) -> list[Task]:
    tasks = []
    for task_config in config.tasks:
        tasks.append(
            Task(
                CronTrigger.from_crontab(task_config.schedule), 
                handler.TaskHandler(
                    prober=CONFIG_GENERATOR_MAPPING[type(config)](config, task_config)
                ), task_config.name()
            )
        )
    return tasks

def create_scheduler(config: config.Config) -> BaseScheduler | None:
    # we do not allow parallel executions as these might influence measurements on other executors.
    executors = {
        "default": ThreadPoolExecutor(max_workers=1)
    }

    validation = config.validate()
    if not validation.valid:
        logger.error(f"Invalid configuration: {"\n".join(validation.errors)}")
        return None

    if config.influx is None:
        logger.error("InfluxDB configuration is required")
        return None

    influx_client = influx.InfluxClient(config.influx)
    common_handlers = [handler.LogHandler(), handler.InfluxHandler(influx_client)]
    tasks: list[Task] = []
    if config.ping:
        tasks.extend(to_jobs(config.ping, common_handlers))
    if config.iperf:
        tasks.extend(to_jobs(config.iperf, common_handlers))
    if config.speedtest:
        tasks.extend(to_jobs(config.speedtest, common_handlers))

    logger.info(f"found {len(tasks)} handlers")

    scheduler = BlockingScheduler(executors=executors)

    for task in tasks:
        if task.trigger is None:
            raise Exception("Schedule not defined")
        
        scheduler.add_job(
            task.handler.execute,
            task.trigger,
            max_instances=1,
            misfire_grace_time=config.grace_time,
            name=task.name
        )

    return scheduler
