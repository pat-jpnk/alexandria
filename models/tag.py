from db import db


class TagModel(db.Model):              
    __tablename__ = "Tags"
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.String, unique=True, nullable=False)
    tag = db.Column(db.String(128), nullable=False, unique=True)
    books = db.relationship("BookModel", back_populates="tags", secondary="Booktags")
