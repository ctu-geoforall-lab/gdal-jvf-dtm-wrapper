from contextlib import AbstractContextManager

class GdalJvfDtmWrapper(AbstractContextManager['GdalJvfDtmWrapper']):
    def __init__(self, filename):
        self._filename = filename

    def __enter__(self):
        """Enter context manager protocol.
        """
        super().__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager protocol.
        """
        super().__exit__(exc_type, exc_val, exc_tb)
        
