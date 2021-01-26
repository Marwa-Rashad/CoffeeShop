import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase

!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()


## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        available_drinks = Drink.query.all()
        drinks = [drink.short() for drink in available_drinks]
        return jsonify({
  'success': True,
  'drinks': drinks
}), 200
    except:
        db.session.rollback()
        abort(400)
    finally:
      db.session.close()

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(token):
    try:
        available_drinks = Drink.query.all()
        drinks = [drink.long() for drink in available_drinks]
        return jsonify({
  'success': True,
  'drinks': drinks
}), 200
    except:
        db.session.rollback()
        abort(401)
    finally:
      db.session.close()



'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(token):
    data = request.get_json()
    if 'title' and 'recipe' not in data:
        abort(422)
    try: 
        drink = Drink(title=data.get('title'), recipe=json.dumps(data.get('recipe')))
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': [Drink.long(drink)]
        }),200
    except:
        db.session.rollback()
        abort(401)
    finally:
      db.session.close()


'''
@TODO implement endpoint
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
def edit_drink(token, id):
    data = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    try:
        if data.get('title'):
            title = data.get('title') 
            drink.title = title
        if data.get('recipe'):
            recipe = data.get('recipe')
            drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [Drink.long(drink)]
        }), 200
    except:
        db.session.rollback()
        abort(401)
    finally:
      db.session.close()


'''
@TODO implement endpoint
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
def delete_drink(token, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            'success': True,
            "delete": id
        }), 200
    except:
        db.session.rollback()
        abort(401)
    finally:
      db.session.close()


'''
## Error Handling
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False, 
        "error": 401,
        "message": "User is unauthorized to make this action"
        }), 401

@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unable to process the contained instructions"
        }), 422

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "The server cannot or will not process the request due to something that is perceived to be a client error"
        }), 400

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "The server encountered an unexpected condition that prevented it from fulfilling the request"
        }), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "Method not allowed"
        }), 405


@app.errorhandler(AuthError)
def authentification_failed(ex):
    return jsonify({
        "success": False,
        "error": AuthError.status_code,
        "message": ex.error['code']
                    }), 401
'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
            jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

@TODO implement error handler for 404
    error handler should conform to general task above 
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
