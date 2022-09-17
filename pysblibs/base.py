import logging


class Base:
    def __init__(self, *args, logger=None, **kwargs):
        self._logger = logger
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
            formatter = logging.Formatter(
                "(%(asctime)s) [%(levelname)s:%(module)s:%(lineno)d]: %(message)s",
                "%H:%M:%S")
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(stream_handler)