from flask import jsonify

def make_response(success=True, data=None, message='', status=200):
    return jsonify({
        'success': success,
        'data': data,
        'message': message,
        'code': status
    }), status

def make_response_dict(success=True, data=None, message='', status=200):
    return {
        'success': success,
        'data': data,
        'message': message,
        'code': status
    }
