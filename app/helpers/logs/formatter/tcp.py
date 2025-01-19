import json
from logging.handlers import SocketHandler


class TCPLogFormatter(SocketHandler):
    """
    A log formatter for TCP socket handlers.

    This class extends the SocketHandler to format log records into JSON
    and encode them for transmission over a TCP socket.

    Methods:
        makePickle(record):
            Formats the log record as a JSON string, appends a newline,
            and encodes it as UTF-8 bytes.
    """

    def makePickle(self, record):
        log_entry = json.loads(self.format(record))
        return (json.dumps(log_entry) + "\n").encode("utf-8")
