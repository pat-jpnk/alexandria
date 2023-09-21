from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from schemas import TagSchema, TagUpdateSchema, PlainTagSchema, TagSearchQueryArgs
from models import TagModel
from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import link_id as lid

blp = Blueprint("Tags", __name__, description="Tag resource")


@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @jwt_required()
    @blp.response(200, TagSchema, description="success - tag found")
    @blp.alt_response(404, description="tag not found")
    def get(self, tag_id):
        """list single tag"""  
        tag = TagModel.query.filter_by(link_id = tag_id).first()      

        if not tag:
            abort(404, message="tag not found")

        return tag
    
    # TODO: read docs about extra decorator fields
    # INFO: Deleting tag cascade deletes all related fields in Booktags table

    # INFO: SQLAlchemy gives error when trying to delete entity from many-to-many relationship: 
    # example: AssertionError: Dependency rule tried to blank-out primary key column 'cart_products_association.cart_id' on instance '<CartProductsAssociation at 0x7f5fd41721d0>'
    
    # TODO: INCLUDE DELETE WARNING

    #https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#deleting-rows-from-the-many-to-many-table
    
    #@jwt_required(fresh=True)
    @blp.response(202, description="accepted - tag deleted")
    @blp.alt_response(404, description="tag not found")
    def delete(self, tag_id):
        """delete tag"""
        tag = TagModel.query.filter_by(link_id = tag_id).first()  

        if tag:
            try:
                db.session.delete(tag)
                db.session.commit()
            except SQLAlchemyError:
                abort(500, message="error occurred during tag deletion")
        else:
            abort(404, message="tag not found")

        return {"code": 200,"message": "tag deleted successfully"}

    @jwt_required(fresh=True)
    @blp.arguments(TagUpdateSchema)
    @blp.response(204, TagSchema,  description="success, no content - tag modified")
    @blp.alt_response(409, description="database constraint violation")
    @blp.alt_response(404, description="tag not found")
    def put(self, tag_data, tag_id): 
        """modify tag"""                           # made idempotent, why ? (https://www.rfc-editor.org/rfc/rfc9110#PUT)
        #tag = TagModel.query.get(tag_id)              # if we allow creation with user supplied id, user determines id, if we generate id randomly
      
        tag = TagModel.query.filter_by(link_id = tag_id).first()  
        if tag:                                             # then the request is not idempotent anymore
            tag.tag = tag_data["tag"]

            try:
                db.session.add(tag)
                db.session.commit()
            except IntegrityError:
                abort(409, message="error, database constraint violation occured")      # TODO: add more info, justify 409
            except SQLAlchemyError:
                abort(500, message="error occured during tag insertion")
        else:
            abort(404, message="tag not found")
        
        return tag


# https://www.rfc-editor.org/rfc/rfc9110#name-content-location
# " response contains the new representation of that resource"




@blp.route("/tags")
class TagList(MethodView):
   # @jwt_required() RE ENABLE
    @blp.arguments(TagSearchQueryArgs, location="query")
    @blp.response(200, TagSchema(many=True),  description="success - tags found")
    def get(self, search_value):
        """list multiple tags"""

        name = search_value.get("name")
        result = TagModel.query

        if name:
            result = result.filter(TagModel.tag.contains(search_value.get("name")))

        return result
        
    @jwt_required(fresh=True)
    @blp.arguments(PlainTagSchema)
    @blp.response(201, TagSchema,  description="created - tag created")
    @blp.alt_response(409, description="database constraint violation")
    def post(self, tag_data):
        """add tag"""
        tag_data["link_id"] = lid.get_link_id()
        tag = TagModel(**tag_data)      # turn dict into keyword arguments

        try:
            db.session.add(tag)
            db.session.commit()
        except IntegrityError:
            abort(409, message="error, database constraint violation occured")
        except SQLAlchemyError:
            abort(500, message="error occured during tag insertion")

        return tag
