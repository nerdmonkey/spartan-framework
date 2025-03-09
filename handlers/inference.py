from app.helpers.environment import env
from app.helpers.logger import get_logger

logger = get_logger("spartan-framework")


def main():
    environment = env().APP_ENVIRONMENT
    logger.info(f"Currently in {environment} environment")
    logger.info("Hello, from Spartan")

    return {
        "status_code": 200,
    }


if __name__ == "__main__":
    result = main()
    logger.info("response", extra={"result": result})
