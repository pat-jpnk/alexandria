from marshmallow import Schema, fields, validate


class PlainBookSchema(Schema):
    link_id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    added_at = fields.Str(required=True)                     #fields.DateTime(format="iso,required=True) # ISO 8601 # dump_only=True  required=True
    release_year = fields.Int(validate=lambda x: x > 0)
    completed = fields.Int(validate=validate.OneOf([0,1]))
    bookmarked = fields.Int(validate=validate.OneOf([0,1]))
    active = fields.Int(validate=validate.OneOf([0,1]))
    file_url = fields.URL(dump_only=True)

class PlainTagSchema(Schema):
    link_id = fields.Str(dump_only=True)
    tag = fields.Str(required=True)

class TagSchema(PlainTagSchema):
    books = fields.List(fields.Nested(PlainBookSchema()), dump_only=True)

class TagUpdateSchema(Schema):
    tag = fields.Str()

class BookSchema(PlainBookSchema):
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class BookUpdateSchema(Schema):
    title = fields.Str()
    release_year = fields.Int(validate=lambda x: x > 0)
    completed = fields.Int(validate=validate.OneOf([0,1]))
    bookmarked = fields.Int(validate=validate.OneOf([0,1]))
    active = fields.Int(validate=validate.OneOf([0,1]))

class PlainUserSchema(Schema):
    link_id = fields.Str(dump_only=True)
    user_name = fields.Str(required=True)
    email = fields.Email(required=True, validate=validate.Email())


class UserSchema(PlainUserSchema):
    user_password = fields.Str(required=True, load_only=True) 

class UserUpdateSchema(Schema):
    email = fields.Email(required=True, validate=validate.Email())
    user_password = fields.Str(required=True, load_only=True)               # change ?

class UserLoginSchema(Schema):
    user_name = fields.Str(required=True)
    user_password = fields.Str(required=True, load_only=True)               


class BooktagSchema(Schema):
    message = fields.Str()
    book = fields.Nested(PlainBookSchema)
    tag = fields.Nested(PlainTagSchema)

class MultipartFileSchema(Schema):
    file = fields.Raw(required=True)                     # metadata={"type": "file"}