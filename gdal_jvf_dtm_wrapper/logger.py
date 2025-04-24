import os
import logging
import logging.config

class GdalJvfDtmWrapperLogger(logging.getLoggerClass()):
    pass

def logger():
    logging.config.fileConfig(
        os.path.join(os.path.dirname(__file__), 'logging.conf')
    )

    logger = logging.getLogger('GdalJvfDtmWrapper')

    return logger

Logger = logger()
