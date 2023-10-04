from flask import Blueprint
from flask import jsonify, abort, request
from flask_restful import Api, Resource, reqparse
from datetime import datetime
from flask_cors import cross_origin
from functools import wraps
import os
from .interface import InterfaceWallet
from .backend import Api

# Blueprint Configuration
auth = Blueprint('details_api', __name__)
VERSION = "1.0"
# Here api key provided to the server A for send reqeset 
api_key = "bcb19744374c60ca8874cc5039eab687"
unauth_data = {
    "status": "error",
    "message": "You are not authorized"
}



# RESTful API
class api_details(Resource):

    @cross_origin(supports_credentials=True)
    def get(self):
        if not request.headers.get('key') == api_key:
                return jsonify(unauth_data), 401
        data = {"version": VERSION, "endpoint": "api_get_transaction"}
        return jsonify(data),200


class api_get_transaction(Resource):
    @cross_origin(supports_credentials=True)
    def get(self):
        try:
            if not request.headers.get('key') == api_key:
                return jsonify(unauth_data), 401

            data = {"version": VERSION, "endpoint": "api_get_transaction"}
            return jsonify(data), 200
        except Exception as e:
            print ("Error getting log", str(e))
            return {'error': str(e)}, 500

    @cross_origin(supports_credentials=True)
    def post(self):
        columns = ["account_id", "page_no"]
        parser = reqparse.RequestParser()
        for column in columns:
            parser.add_argument(column, required=True)
        args = parser.parse_args()
        try:
            if not request.headers.get('key') == api_key:
                return jsonify(unauth_data), 401
            api = Api()
            result = api.get_transactions(args["account_id"], args["page_no"] )
            return jsonify(result), 200
        except Exception as e:
            print ("Error getting transactions", str(e))
            return {'error': str(e)}, 500

class api_get_balance(Resource):
    @cross_origin(supports_credentials=True)
    def get(self):
        try:
            if not request.headers.get('key') == api_key:
                return jsonify(unauth_data), 401
            api = Api()
            result = api.get_balance(None)
            return jsonify(result), 200
        except Exception as e:
            print ("Error getting log", str(e))
            return {'error': str(e)}, 500

class api_card_control(Resource):
    @cross_origin(supports_credentials=True)
    def get(self):
        try:
            if not request.headers.get('key') == api_key:
                return jsonify(unauth_data), 401
            result = {"version": VERSION, "endpoint": "api_card_control"}
            return jsonify(result), 200
        except Exception as e:
            print ("Error getting api_card_control", str(e))
            return {'error': str(e)}, 500

    @cross_origin(supports_credentials=True)
    def post(self):
        columns = ["card_number", "action"]
        parser = reqparse.RequestParser()
        for column in columns:
            parser.add_argument(column, required=True)
        args = parser.parse_args()
        try:
            if not request.headers.get('key') == api_key:
                return jsonify(unauth_data), 401
            api = Api()
            result = api.control_card(args["card_number"], args["action"] )
            return jsonify(result), 200
        except Exception as e:
            print ("Error performing card action", str(e))
            return {'error': str(e)}, 500


class api_transfer_amount(Resource):
    @cross_origin(supports_credentials=True)
    def get(self):
        try:
            if not request.headers.get('key') == api_key:
                return jsonify(unauth_data), 401
            result = {"version": VERSION, "endpoint": "api_transfer_amounts"}
            return jsonify(result), 200
        except Exception as e:
            print ("Error getting api_transfer_amount", str(e))
            return {'error': str(e)}, 500

    @cross_origin(supports_credentials=True)
    def post(self):
        columns = ["from_account", "to_account", "amount", "note"]
        parser = reqparse.RequestParser()
        for column in columns:
            parser.add_argument(column, required=True)
        args = parser.parse_args()
        try:
            if not request.headers.get('key') == api_key:
                return jsonify(unauth_data), 401
            api = Api()
            result = api.do_transfer(args["from_account"], args["to_account"], args["amount"], args["note"] )
            return jsonify(result), 200
        except Exception as e:
            print ("Error in transfer amount", str(e))
            return {'error': str(e)}, 500

class api_card_status(Resource):
    @cross_origin(supports_credentials=True)
    def get(self):
        try:
            if not request.headers.get('key') == api_key:
                return jsonify(unauth_data), 401
            result = {"version": VERSION, "endpoint": "api_card_status"}
            return jsonify(result), 200
        except Exception as e:
            print ("Error getting api_card_status", str(e))
            return {'error': str(e)}, 500

    @cross_origin(supports_credentials=True)
    def post(self):
        columns = ["card_number"]
        parser = reqparse.RequestParser()
        for column in columns:
            parser.add_argument(column, required=True)
        args = parser.parse_args()
        try:
            if not request.headers.get('key') == api_key:
                return jsonify(unauth_data), 401
            api = Api()
            result = api.status_card(args["card_number"] )
            return jsonify(result), 200
        except Exception as e:
            print ("Error api_card_status", str(e))
            return {'error': str(e)}, 500