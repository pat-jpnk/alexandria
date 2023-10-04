from db import db


class UserModel(db.Model):            
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.String(128), unique=True, nullable=False)
    user_name = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    user_password = db.Column(db.String(128), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, unique=False, nullable=False)
    verified_email = db.Column(db.Boolean, nullable=False)