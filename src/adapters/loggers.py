import logging

logger = logging.getLogger("budget_analyse")

if not logger.handlers: 
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

logger.propagate = False
