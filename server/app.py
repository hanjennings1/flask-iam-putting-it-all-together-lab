#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe, UserSchema, RecipeSchema


# SIGN-UP CLASS ----
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


# CHECK SESSION ----
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')                         # None if no one is logged in

        if user_id:                                              # truthy check also catches user_id = None
            user = User.query.filter(User.id == user_id).first() # look up the logged-in user
            if user:
                return UserSchema().dump(user), 200              # user JSON + 200 OK

        return {'errors': ['Unauthorized']}, 401                 # not logged in (or user no longer exists)
    

# LOGIN FEATURE ----
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter(User.username == username).first()  # None if no such username

        if user and user.authenticate(password):     # user exists AND password matches the hash
            session['user_id'] = user.id             # login the user
            return UserSchema().dump(user), 200      # user JSON + 200 OK

        return {'errors': ['Invalid username or password.']}, 401   # if wrong username or password


# LOGOUT FEATURE ----
class Logout(Resource):
    def delete(self):
        if session.get('user_id'):                  # if someone is logged in
            session.pop('user_id', None)            # remove their ID (logs them out)
            return {}, 204                          # empty response + 204 No Content

        return {'errors': ['Unauthorized']}, 401    # no one to log out


# RECIPE FEATURE ----
class RecipeIndex(Resource):
    # LIST OUT THE RECIPES --
    def get(self):
        if session.get('user_id'):                                # only logged-in users can view recipes
            recipes = Recipe.query.all()                          # every recipe in the database
            return RecipeSchema(many=True).dump(recipes), 200     # list of recipe dicts + 200 OK

        return {'errors': ['Unauthorized']}, 401                  # not logged in

    # CREATE A NEW RECIPE --
    def post(self):
        user_id = session.get('user_id')
        if not user_id:                                         # must be logged in to create a recipe
            return {'errors': ['Unauthorized']}, 401

        data = request.get_json()

        try:
            recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),          # validator runs here
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=user_id,                                # recipe belongs to the logged-in user
            )
            db.session.add(recipe)
            db.session.commit()
            return RecipeSchema().dump(recipe), 201             # new recipe with nested user + 201 Created

        except ValueError as e:                                 # if onstructions missing or under 50 chars
            db.session.rollback()
            return {'errors': [str(e)]}, 422

        except IntegrityError:                                  # if title missing (nullable=False)
            db.session.rollback()
            return {'errors': ['Title is required.']}, 422

    

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)