import multiprocessing
import logging

logger = logging.getLogger(__name__)

def configure_multiprocessing():
    try:
        multiprocessing.set_start_method("spawn", force=True)
        logging.info("Multiprocessing start method set to 'spawn'")
    except RuntimeError as e:
        logging.info(f"Multiprocessing start method not set: {e}")