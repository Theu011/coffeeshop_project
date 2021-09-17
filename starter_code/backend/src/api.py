from enum import auto
import os
from typing import final
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import json
from flask_cors import CORS
from sqlalchemy.sql.sqltypes import Date

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, get_token_auth_header, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db = SQLAlchemy()

'''
!! Uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks_data = Drink.query.all()
    drinks = [drink.short() for drink in drinks_data]
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        drinks_data = Drink.query.all()
        drinks = [drink.long() for drink in drinks_data]
        return jsonify({
            'sucess': True,
            'drinks': drinks
        }), 200
    except:
        abort(422)

'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    title = request.get_json()['title']
    recipe = request.get_json()['recipe']
    try:
        drink_item = Drink(
            title=title,
            recipe=json.dumps(recipe)
        )
        drink_item.insert()

        return jsonify({
            'success': True, 
            'drinks': [drink_item.long()]
        }), 200
    except Exception:
        print(Exception)
        abort(422)

'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    title = request.get_json()['title']
    recipe = request.get_json()['recipe']
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink == None:
            abort(404)
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()

        return jsonify({
            'success': True, 
            'drinks': [drink.long()]
        }), 200
    except Exception as e:
        print(e)
        abort(422)
'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink == None:
            abort(404)
        drink.delete()

        return jsonify({
            'sucess': True,
            'delete': id
        }), 200
    except Exception as e:
        print(e)
        abort(422)

# Error Handling

# 422 error unprocessable request
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


# 404 error resource not found
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "resource not found"
    }), 404

# authentication error authentication failed
@app.errorhandler(AuthError)
def auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
