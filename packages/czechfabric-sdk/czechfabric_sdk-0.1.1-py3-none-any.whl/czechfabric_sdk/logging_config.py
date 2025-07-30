import logging

logger = logging.getLogger("czechfabric_sdk")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)
