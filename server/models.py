from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields

from config import db, bcrypt

# USER MODEL ----
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)                    # auto-assigned unique ID
    username = db.Column(db.String, unique=True, nullable=False)    # required, no duplicates
    _password_hash = db.Column(db.String)                           # stores the bcrypt hash, never plain text
    image_url = db.Column(db.String)                                # optional profile image
    bio = db.Column(db.String)                                      # optional user bio

    recipes = db.relationship('Recipe', back_populates='user')      # user.recipes -> list of this user's recipes

    # PASSWORD LOGIC ----
    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')         # reading is blocked on purpose

    @password_hash.setter
    def password_hash(self, password):
        hashed = bcrypt.generate_password_hash(password.encode('utf-8'))  # scramble the plain-text password
        self._password_hash = hashed.decode('utf-8')                      # store the hash as a string

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))  # True if password matches


# RECIPE MODEL ----
class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)                     # auto-assigned unique ID
    title = db.Column(db.String, nullable=False)                     # required
    instructions = db.Column(db.String, nullable=False)              # required (50-char rule added in Step 2)
    minutes_to_complete = db.Column(db.Integer)                      # optional cook time

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))       # links recipe to its user; nullable for tests
    user = db.relationship('User', back_populates='recipes')         # recipe.user -> the User who owns it

    # VALIDATION ----
    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions or len(instructions) < 50:                     # missing or too short(50-char min)
            raise ValueError('Instructions must be at least 50 characters long.')
        return instructions                                                # valid; save it


# SCHEMA CLASSES ----
class UserSchema(Schema):
    id = fields.Int()               # included in JSON
    username = fields.Str()
    image_url = fields.Str()
    bio = fields.Str()
    # _password_hash is left out on purpose, so it's never sent

class RecipeSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    instructions = fields.Str()
    minutes_to_complete = fields.Int()
    user = fields.Nested(UserSchema)  # includes the recipe's user as a nested object