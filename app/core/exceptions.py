class AppException(Exception):
    def __init__(self, message: str, error_code:str, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class BadRequestException(AppException):
    def __init__(self, message: str, error_code: str = "BAD_REQUEST"):
        super().__init__(message, error_code, status_code = 400)

class NotFoundException(AppException):
    def __init__(self, message: str, error_code: str = "NOT_FOUND"):
        super().__init__(message, error_code, status_code=404)

class ConflictException(AppException):
    def __init__(self, message: str, error_code: str = "CONFLICT"):
        super().__init__(message, error_code, status_code=409)

class ServiceUnavailableException(AppException):
    def __init__(self, message: str, error_code: str = "SERVICE_UNAVAILABLE"):
        super().__init__(message, error_code, status_code=503)