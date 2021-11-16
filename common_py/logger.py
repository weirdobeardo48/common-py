import os
import logging
import logging.config


class LoggerUtils:
    def __init__(self) -> None:
        self.init_log()

    def init_log(self):
        # Just a workaround, but whatever, this is just a cheap script
        self.LOG_FILE_PATH = os.getenv('COMMON_PY_LOG_FILE_PATH', './')
        self.LOG_FILE_LEVEL = os.getenv('COMMON_PY_LOG_FILE_LEVEL', 'WARN')
        self.LOG_STDOUT_LEVEL = os.getenv('COMMON_PY_STDOUT_LOG_LEVEL', 'WARN')
        self.LOG_DEFAULT_LEVEL = os.getenv(
            'COMMON_PY_DEFAULT_LOG_LEVEL', 'WARN')
        self.LOG_FILE_ENABLED = os.getenv('COMMON_PY_ENABLE_LOG_FILE', '0')
        handlers = []
        handler = {}

        handler['stdout_handler'] = {
            'class': 'logging.StreamHandler',
            'level': self.LOG_STDOUT_LEVEL,
            'formatter': 'standard'
        }

        handlers.append('stdout_handler')
        if self.LOG_FILE_ENABLED == '1':
            handlers.append('file_handler')
            if os.path.join(self.LOG_FILE_PATH):
                if not os.path.exists(os.path.join(self.LOG_FILE_PATH)):
                    os.makedirs(os.path.join(self.LOG_FILE_PATH))

            handler['file_handler'] = {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': self.LOG_FILE_LEVEL,
                'formatter': 'standard',
                'filename': os.path.join(self.LOG_FILE_PATH, 'application.log'),
                'encoding': 'utf8',
                'backupCount': 10,
                'when': 'd',
                'interval': 1,
            }

        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s [%(processName)s %(threadName)s]: %(lineno)d: %(message)s'
                },
            },
            'handlers': handler,
            'loggers': {
                '': {
                    'handlers': handlers,
                    'level': self.LOG_DEFAULT_LEVEL,
                    'propagate': False
                }
            }
        }
        logging.config.dictConfig(logging_config)
