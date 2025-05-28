from flask import jsonify
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request, check your input'}), 400
    
    @app.errorhandler(409)
    def conflict(error):
        return jsonify({'error': 'Resource already exists'}), 409