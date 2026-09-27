from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields

from config import db, bcrypt

# USER MODEL:
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)                    # auto-assigned unique ID
    username = db.Column(db.String, unique=True, nullable=False)    # required, no duplicates
    _password_hash = db.Column(db.String)                           # stores the bcrypt hash, never plain text
    image_url = db.Column(db.String)                                # optional profile image
    bio = db.Column(db.String)                                      # optional user bio

    recipes = db.relationship('Recipe', back_populates='user')      # user.recipes -> list of this user's recipes


class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)                     # auto-assigned unique ID
    title = db.Column(db.String, nullable=False)                     # required
    instructions = db.Column(db.String, nullable=False)              # required (50-char rule added in Step 2)
    minutes_to_complete = db.Column(db.Integer)                      # optional cook time

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))       # links recipe to its user; nullable for tests
    user = db.relationship('User', back_populates='recipes')         # recipe.user -> the User who owns it

class UserSchema(Schema):
    pass

class RecipeSchema(Schema):
    pass