from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter


class FileLogFormatter(LambdaPowertoolsFormatter):
    """
    FileLogFormatter is a custom log formatter that extends the LambdaPowertoolsFormatter.

    This formatter is designed to format log records for file-based logging.

    Methods:
        format(record):
            Formats the specified log record as text.
            Args:
                record (LogRecord): The log record to be formatted.
            Returns:
                str: The formatted log record as a string.
    """

    def format(self, record):
        return super().format(record)
