import asyncio
import os


def configure_event_loop():
    """
    Configure the event loop for the application.
    This function sets the event loop policy to use asyncio's default event loop.
    """
    try:
        # Set the event loop policy to use asyncio's default event loop
        if os.getenv("ENV", "development") == "production":
            import uvloop

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            print("Event loop configured to use uvloop for production.")
    except Exception as e:
        print(f"Error configuring event loop: {str(e)}")
