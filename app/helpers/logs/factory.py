from app.helpers.logs.logger.console import ConsoleLogger
from app.helpers.logs.logger.file import FileLogger
from app.helpers.logs.logger.tcp import TCPLogger
from app.helpers.environment import env


class LoggerFactory:
    """
    LoggerFactory is a factory class responsible for creating different types of loggers
    based on the application's environment and logging channel.

    Methods:
        create_logger():
            Creates and returns an appropriate logger instance based on the environment
            and logging channel specified in the application's configuration.

            Returns:
                FileLogger: If the environment is 'local' and the logging channel is 'file'.
                TCPLogger: If the environment is 'local' and the logging channel is 'tcp'.
                ConsoleLogger: For all other configurations.
    """
    @staticmethod
    def create_logger():
        app_env = env().APP_ENVIRONMENT
        log_channel = env().LOG_CHANNEL
        if app_env == "local" and log_channel == "file":
            return FileLogger()
        elif app_env == "local" and log_channel == "tcp":
            return TCPLogger()
        else:
            return ConsoleLogger()
