import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# THIS WILL DROP ALL RECORDS AND START DB FROM SCRATCH
# db_drop_and_create_all()

# ROUTES

# drinks endpoint it is public
@app.route('/drinks')
def drinks():
    try:
        # query data and contain only drink.short() data representation
        drinks = Drink.query.all()
        drinks_list = [drink.short() for drink in drinks]
        # return if success
        return jsonify({
            "success": True,
            "drinks": drinks_list
        }), 200
    # failure if any exception
    except Exception as e:
        # print(e)
        abort(422)


# drinks_details endpoint it is not public
@app.route('/drinks-detail')
# it is require 'get:drinks-detail' user permission
@requires_auth('get:drinks-detail')
# function drinks_details take payload(jwt token) arguments
def drinks_details(payload):
    try:
        # query data and contain only drink.long() data representation
        drink_query = Drink.query.all()
        drinks = [drink.long() for drink in drink_query]
        # return if success
        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200
    # failure if any exception
    except Exception as e:
        # print(e)
        abort(422)


# POST /drinks endpoint for Add new data in Drink database
@app.route('/drinks', methods=['POST'])
# it is require 'post:drinks' user permission
@requires_auth('post:drinks')
def new_drinks(payload):
    try:
        # get data input
        data = request.get_json()
        # if data and recipe not in data input raise error
        if 'title' and 'recipe' not in data:
            abort(404)
        # get title, recipe data from user data input
        title = data['title']
        recipe = data['recipe']
        # check recipe is list format or not
        recipe_isinstance = recipeisinstance(recipe)
        # Insert into table where value is taking from user input
        newDrink = Drink(title=title, recipe=json.dumps(recipe_isinstance))
        # insert into database
        newDrink.insert()
        # return array of containing only the newly created drink
        return jsonify({
            "success": True,
            "drinks": [newDrink.long()]
        }), 200
    # raise error if any failure
    except Exception as e:
        # print(e)
        abort(422)


# PATCH /drinks endpoint for update data for given drink id.
@app.route('/drinks/<int:id>', methods=['PATCH'])
# it is require 'patch:drinks' user permission
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    try:
        # get data from user input
        data = request.get_json()
        # Fetch Drink data row filter_by drink id.
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        # if drink is None raise error
        if drink is None:
            abort(404)
        # check title and recipe in user input and respectively update.
        if 'title' in data:
            drink.title = data['title']
        if 'recipe' in data:
            # check recipe is list format or not
            recipe_isinstance = recipeisinstance(data['recipe'])
            # json.dumps used for take json object and return in string
            drink.recipe = json.dumps(recipe_isinstance)
        # finally update data
        drink.update()
        # return array of containing only the updated drink
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    # raise if any error
    except Exception as e:
        # print(e)
        abort(422)


# DELETE drinks/id - endpoint, delete drinks by given id.
@app.route('/drinks/<int:id>', methods=['DELETE'])
# it is require 'patch:drinks' user permission
@requires_auth('delete:drinks')
# take arguments payload and id
def delete_drinks(payload, id):
    try:
        # Fetch Drink data row filter_by drink id.
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        # if drink is None raise error
        if drink is None:
            abort(422)
            # delete corresponding row of given id
        drink.delete()
        # return if success
        return jsonify({
            "success": True,
            "delete": id
        }), 200
    # raise error
    except Exception as e:
        # print(e)
        abort(422)


# Error Handling

# bad request error handler
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": false,
        "error": 400,
        "message": "bad request"
    }), 400


# Not Found error Handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


# Method not allowed error handler
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


# unprocessable error Handler
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


# Auth error Handler
@app.errorhandler(AuthError)
def autherrorhandling(error):
    status_code = error.status_code
    message = error.error
    return jsonify({
        "success": False,
        "error": status_code,
        "message": message['description']
    }), status_code


# check given recipe is list format or not
# if not then return list of recipe
def recipeisinstance(recipe):
    return [recipe] if not isinstance(recipe,  list) else recipe
