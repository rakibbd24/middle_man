#!/usr/local/bin/python3.9
from flask import Flask
from flask_restful import Api
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    # Using a development configuration
    app.config.from_object('config.DevConfig')

    # Api
    api = Api(app)

    with app.app_context():

        from blueprints.details_api import api_details, api_get_transaction, api_get_balance, api_card_control, api_transfer_amount, api_card_status
       
        # Add Api URL endpoint
        api.add_resource(api_details, '/api/details/')
        api.add_resource(api_get_transaction, '/api/transaction/')
        api.add_resource(api_get_balance, '/api/mainbalance/')
        api.add_resource(api_card_control, '/api/control/')
        api.add_resource(api_transfer_amount, '/api/transfer/')
        api.add_resource(api_card_status, '/api/cardstatus/')

        return app

