def main(event, context):
    """Entry point for Google Cloud Functions."""
    from handlers.inference import main as inference_main
    return inference_main(event, context)
