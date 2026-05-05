import sys
import logging
from cli import parse_args
from config import Config
from scheduler import create_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

def main():
    args = parse_args()
    
    if args.log_level:
        logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
    Config.from_cli_args(args)
    
    errors = Config.validate()
    if errors:
        for error in errors:
            logging.error("Configuration error: %s", error)
        sys.exit(1)
    
    if args.dry_run:
        logging.info("Configuration valid. Exiting (--dry-run mode)")
        sys.exit(0)
    
    scheduler = create_scheduler()
    if scheduler is None:
        sys.exit(1)
    
    scheduler.start()

if __name__ == "__main__":
    main()
