from datetime import datetime, timezone

def get_timestamp():
    return {
        "timestamp": datetime.now(timezone.utc).isoformat()
    }