import logging

# Createng a logger
logger = logging.getLogger("scraper")
logger.setLevel(logging.DEBUG)



# Creating a formatter
# Creating a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Creating a stream handler and set its level to DEBUG
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

# Addding stream handler to the logger
logger.addHandler(stream_handler)