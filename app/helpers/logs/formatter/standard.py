from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter


class StandardLogFormatter(LambdaPowertoolsFormatter):
    def format(self, record):
        return super().format(record)
