from db import db


class BookModel(db.Model):                   
    __tablename__ = "Books"
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String(128), unique=False, nullable=False)
    added_at = db.Column(db.String(128), unique=False, nullable=False)
    release_year = db.Column(db.Integer, nullable=True, unique=False)
    completed = db.Column(db.Boolean, nullable=False, unique=False)
    bookmarked = db.Column(db.Boolean, nullable=False, unique=False)
    active = db.Column(db.Boolean, nullable=False, unique=False)
    file_url = db.Column(db.String(128), unique=False, nullable=True)
    tags = db.relationship("TagModel", back_populates="books", secondary="Booktags")
