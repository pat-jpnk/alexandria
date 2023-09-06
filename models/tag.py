from db import db


class TagModel(db.Model):              # mapping of row in table to python class
    __tablename__ = "Tags"
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.String, unique=True, nullable=False)
    tag = db.Column(db.String(128), nullable=False, unique=True)

    # not using  lazy="dynamic"
    books = db.relationship("BookModel", back_populates="tags", secondary="Booktags")

    # lazy="dynamic", does not populate column until usage -> faster queries