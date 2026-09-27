#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe, UserSchema, RecipeSchema


# SIGN-UP CLASS
class Signup(Resource):
    def post(self):
        data = request.get_json()                    # JSON body sent from the frontend

        user = User(
            username=data.get('username'),           # .get() returns None if missing, instead of crashing
            image_url=data.get('image_url'),
            bio=data.get('bio'),
        )
        user.password_hash = data.get('password')    # runs the setter, which hashes the password

        try:
            db.session.add(user)
            db.session.commit()                      # IntegrityError here if username is missing or taken
            session['user_id'] = user.id             # login the new user
            return UserSchema().dump(user), 201      # user JSON + 201 Created

        except IntegrityError:
            db.session.rollback()                    # undo the failed save so the session stays usable
            return {'errors': ['Username is required and must be unique.']}, 422

class CheckSession(Resource):
    pass

class Login(Resource):
    pass

class Logout(Resource):
    pass

class RecipeIndex(Resource):
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)