class UnauthorizedError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class TokenExpiredError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class BadRequestError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NotFoundError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InternalServerError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
