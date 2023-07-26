"""Setup and run a simple echo bot."""
import logging
import os

if os.getenv("ENV") != "production":
    # Get EV from a local .env file
    from dotenv import load_dotenv

    load_dotenv()

from src import application

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    application.initialize()
    application.register_handlers()
    application.run()


if __name__ == "__main__":
    main()
