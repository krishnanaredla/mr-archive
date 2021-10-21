import logging


def SquirrelLogger():
    logFormatter = logging.Formatter(fmt=" %(name)s :: %(levelname)-8s :: %(message)s")
    logger = logging.getLogger("Squirrel")
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    return logger
