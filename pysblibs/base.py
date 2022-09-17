import logging


class Base:
    def __init__(self, *args, logger=None, **kwargs):
        self._logger = logger
        if self._logger is None:
            self._logger = logging.getLogger(__name__)