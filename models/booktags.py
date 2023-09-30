from db import db


class BooktagModel(db.Model):              
    __tablename__ = "Booktags"
    book_id = db.Column(db.Integer, db.ForeignKey('Books.id'), primary_key=True, unique=False, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('Tags.id'), primary_key=True, unique=False, nullable=False)
