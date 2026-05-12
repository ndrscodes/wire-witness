import sys
import os
import logging
from cli import parse_args
from config import Config, ConfigLoader
from scheduler import create_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


def main():
    args = parse_args()

    if args.log_level:
        logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    config = Config()
    config_file = args.config_file or os.environ.get("WIREWITNESS_CONFIG_FILE")
    if config_file:
        logger.info("loading config from file %s", config_file)
        config = ConfigLoader.load_file(config_file)

    config.load(args)

    scheduler = create_scheduler(config)
    if scheduler is None:
        logger.error("unable to create scheduler")
        sys.exit(1)

    scheduler.start()


if __name__ == "__main__":
    main()
