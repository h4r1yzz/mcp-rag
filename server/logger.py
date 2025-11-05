import logging 

def setup_logger(name="Assistant"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch=logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter=logging.Formatter("[%(asctime)s] [%(levelname)s] --- [%(message)s]")
    ch.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(ch)
    return logger

logger = setup_logger()

logger.info("Rag Processor is starting...")
logger.debug("Debugging.")
logger.error("An error occurred.")
logger.critical("Critical error! The system is down!")

