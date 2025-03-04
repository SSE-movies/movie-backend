from src import run_app
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting application...")
    logger.info(f"PORT: {os.getenv('PORT', '5000')}")
    logger.info(
        f"DATABASE_URL: {'set' if os.getenv('DATABASE_URL') else 'not set'}"
    )
    run_app()
