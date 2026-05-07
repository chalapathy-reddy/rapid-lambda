
class HTTPException(Exception):

    def __init__(self, status_code: int, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(str(detail))

class BadRequest(HTTPException):

    def __init__(self, detail):
        super().__init__(400, detail)

class Unauthorized(HTTPException):

    def __init__(self, detail="Unauthorized"):
        super().__init__(401, detail)

class NotFound(HTTPException):

    def __init__(self, detail="Not Found"):
        super().__init__(404, detail)
