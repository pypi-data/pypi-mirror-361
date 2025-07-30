from shared.exceptions import (
    BadRequestError, NotFoundError, ValidationError, 
    UnauthorizedError, TokenExpiredError, InternalServerError
)
from shared.response import make_response

def register_error_handlers(app):
    @app.errorhandler(BadRequestError)
    def handle_bad_request(error):
        print(error)
        return make_response(False, None, str(error), 400)

    @app.errorhandler(NotFoundError)
    def handle_not_found(error):
        return make_response(False, None, str(error), 404)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return make_response(False, None, str(error), 400)

    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized(error):
        return make_response(False, None, str(error), 401)

    @app.errorhandler(TokenExpiredError)
    def handle_token_expired(error):
        return make_response(False, None, str(error), 401)

    @app.errorhandler(InternalServerError)
    def handle_internal_server_error(error):
        return make_response(False, None, str(error), 500)