class PortalError(RuntimeError):
    def __init__(self, type: str, message: str):
        super(PortalError, self).__init__(message)
        self.type = type
        self.message = message


class PortalClientError(PortalError):
    def __init__(self, type: str, message: str, details: str | None = None):
        super(PortalClientError, self).__init__(type, message)
        self.details = details


class PortalApiError(PortalError):
    def __init__(
        self,
        type: str,
        message: str,
        status_code: int,
        details: str | None = None,
    ):
        self.type = type
        self.message = message
        self.status_code = status_code
        self.details = details
        super(PortalApiError, self).__init__(type, message)
