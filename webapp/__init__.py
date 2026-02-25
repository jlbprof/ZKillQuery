from flask import Flask
import math

def create_app():
    app = Flask(__name__)
    app.secret_key = 'zkillboard-query-secret-key'
    
    @app.template_filter('format_number')
    def format_number(value):
        if value is None:
            return '0'
        return f"{int(value):,}"
    
    @app.template_filter('round_up')
    def round_up(value, decimals=1):
        if value is None:
            return '0.0'
        multiplier = 10 ** decimals
        return f"{math.ceil(value * multiplier) / multiplier}"
    
    from webapp import routes
    app.register_blueprint(routes.bp)
    
    return app
