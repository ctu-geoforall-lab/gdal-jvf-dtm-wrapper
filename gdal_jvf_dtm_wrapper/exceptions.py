class GdalJvfDtmWrapperError(Exception):
    def __init__(self, message):
        super().__init__(f"Invalid JVF DTM: {message}")
