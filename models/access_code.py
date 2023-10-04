from db import db 

class AccessCodeModel(db.Model):
    __tablename__ = "AccessCodes"
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.String, unique=True, nullable=False)
    create_at = db.Column(db.String, unique=False, nullable=False)
    deactivated_add = db.Column(db.String, unique=False, nullable=True)
    access_code = db.Column(db.String(128), unique=True, nullable=False) # set string size according to secret size
    active = db.Column(db.Boolean, nullable=False)