from config.app import get_settings

settings = get_settings()

APP_NAME = settings.APP_NAME.lower()
APP_ENVIRONMENT = settings.APP_ENVIRONMENT.lower()
