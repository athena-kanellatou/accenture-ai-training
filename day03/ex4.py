import logging

logging.basicConfig(level=logging.INFO, 
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

logging.debug("Detailed debugging information")
logging.info("Application started")
logging.warning("Disk space is getting low")
logging.error("Could not connect to database")
logging.critical("Application cannot continue")