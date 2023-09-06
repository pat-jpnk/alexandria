from db import db


"""
Date and time types return objects from the Python datetime module.
Most DBAPIs have built in support for the datetime module, with the noted exception of SQLite.
In the case of SQLite, date and time types are stored as strings which are then converted back
to datetime objects when rows are returned.

"""

class BookModel(db.Model):              # mapping of row in table to python class
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

    # not using lazy=dynamic
    tags = db.relationship("TagModel", back_populates="books", secondary="Booktags")
