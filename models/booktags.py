from db import db

# composite primary key
# https://docs.sqlalchemy.org/en/20/core/constraints.html
# https://docs.sqlalchemy.org/en/20/faq/ormconfiguration.html


class BooktagModel(db.Model):              # mapping of row in table to python class
    __tablename__ = "Booktags"
    
    book_id = db.Column(db.Integer, db.ForeignKey('Books.id'), primary_key=True, unique=False, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('Tags.id'), primary_key=True, unique=False, nullable=False)
    #book = db.relationship("BookModel", back_populates="Booktags")
    #tag = db.relationship("TagModel", back_populates="Booktags")
