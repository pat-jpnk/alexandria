import datetime
import gzip
import hashlib

import filetype
import sqlalchemy.sql as sql
from flask import Response
from flask import current_app as app
from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import (Blueprint, Page,  # *  # TODO: test if sufficient
                           abort)
from flask_smorest.fields import Upload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.utils import secure_filename

import link_id as lid
from db import db
from models import BookModel, TagModel
from S3 import s3
from schemas import (BookSchema, BookSearchQueryArgs, BookUpdateSchema,
                     MultipartFileSchema, PlainBookSchema)

blp = Blueprint("Books", __name__, description="Book resource")
blp.DEFAULT_PAGINATION_PARAMETERS = {"page": 1, "page_size": 15, "max_page_size": 100}

class CursorPage(Page):
    @property
    def item_count(self):
        return self.collection.count()

@blp.route("/book/<string:book_id>")
class Book(MethodView):
    @jwt_required()
    @blp.response(200, BookSchema)
    @blp.alt_response(404, description="book not found")
    def get(self, book_id):
        """list single book"""
        book = BookModel.query.filter_by(link_id = book_id).first()    

        if not book:
            abort(404, message="book not found")
  
        return book

    @jwt_required(fresh=True)
    @blp.response(204, description="accepted - book deleted")
    @blp.alt_response(404, description="book not found")
    def delete(self, book_id):
        """delete book"""
        jwt = get_jwt()

        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

        book = BookModel.query.filter_by(link_id = book_id).first()

        if book:
            file_url_parts = book.file_url.split('/')          
            blob_key = file_url_parts[4]

            response = s3.delete_object (
                Bucket = "alexandria-api",
                Key = blob_key
            )

            response_data = response.get("ResponseMetaData")
            if response_data is None:
                abort(500, message="error occured during S3 file deletion")
            else:
                if response_data.get("HTTPStatusCode") == 204:
                    try:
                        db.session.delete(book)
                        db.session.commit()
                    except SQLAlchemyError:
                        abort(500, message="error occurred during book deletion")                    
                else:
                    abort(500, message="error occured during S3 file deletion")
        else:
            abort(404, message="book not found")

        return {"code": 204,"message": "book deleted successfully"}
    
    @jwt_required(fresh=True)
    @blp.arguments(BookUpdateSchema)
    @blp.response(204, BookSchema,  description="success, no content - tag modified")
    @blp.alt_response(409, description="database constraint violation")
    @blp.alt_response(404, description="book not found")
    def put(self, book_data, book_id):           
        """modify book"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

        book = BookModel.query.filter_by(link_id = book_id).first()    

        if book:
            book.title = book_data["title"]
            book.release_year = book_data["release_year"]
            book.completed = book_data["completed"]
            book.bookmarked = book_data["bookmarked"]
            book.active = book_data["active"]

            try:
                db.session.add(book)
                db.session.commit()
            except IntegrityError:
                abort(409, message="error, database constraint violation occured")      
            except SQLAlchemyError:
                abort(500, message="error occured during tag insertion")

        else:
            abort(404, message="book not found")

        return book

@blp.route("/book/<string:book_id>/file")
class BookFile(MethodView):
    @jwt_required()
    @blp.response(200)
    @blp.alt_response(404, description="book not found")
    def get(self, book_id):
        """get book file"""
        book = BookModel.query.filter_by(link_id = book_id).first()
        
        if book:
            file_url_parts = book.file_url.split('/')
            blob_key = file_url_parts[4]

            try:
                book_file = s3.get_object(
                    Bucket = 'alexandria-api', 
                    Key = blob_key)['Body'].read()
            except ClientError as e:
                if e.response["Error"]["Code"] == 'InvalidObjectState':
                    abort(500, message="error, S3 object is archived and inaccessible")
                elif e.response["Error"]["Code"] == 'NoSuchKey':
                    abort(500, message="error, no S3 object with given key")
                else:
                    abort(500, message="unknown S3 error occurred")

            book_file = gzip.decompress(book_file)
            
            match book.mime_type:
                case "application/pdf":
                    file_name_extension = ".pdf"
                case "application/epub+zip":
                    file_name_extension = ".epub"
                case _:
                    file_name_extension = ""

            file_name = book.title.replace(" ", "_") + file_name_extension

            response = Response(book_file, mimetype="application/pdf")
            response.headers.set("Content-Disposition", "attachment", filename=file_name)
            
            return response
        else:
            abort(404, message="error, book not found")

    @jwt_required()
    @blp.response(204, description="success, file modified")
    #@blp.alt_response()
    @blp.arguments(MultipartFileSchema, location="files")
    def put(self, files, book_id):
        """modify book file"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

        book_file = files["file"]                       # <class 'werkzeug.datastructures.FileStorage'>

        '''check file size'''
        book_file.seek(0,2)
        if book_file.tell() > app.config["MAX_FILE_SIZE"]:
            abort(413, message="error, file too large")
        book_file.seek(0,0)
        
        '''check content type'''
        content_type = book_file.headers.get('Content-Type')

        if not content_type:
            abort(400, message="error, Content-Type header required")


        file_type = filetype.guess(book_file.read()) # TODO: try, catch typeError
        book_file.seek(0)

        if file_type:
            if file_type.mime in app.config["FILE_FORMATS"]:
                if file_type.mime != content_type:
                    abort(422, message="error, inferred file type differs from Content-Header")
            else:
                abort(415, message="error, unsupported file type")
        else:
            abort(422, message="error, file type indeterminate")

        '''compress file'''
        book_file = gzip.compress(book_file.read())

        '''get MD5 hash'''
        book_file_md5 = hashlib.md5(book_file).hexdigest()
        book = BookModel.query.filter_by(link_id = book_id).first()    

        # check for None

        if book:
            file_url_parts = book.file_url.split('/')            # check if surely there 
            blob_key = file_url_parts[4]

            response = s3.put_object(
                Bucket = "alexandria-api",
                Key = blob_key,
                Body = book_file,
                ContentType = content_type
            )
            
            response_data = response.get("ResponseMetadata")
            if response_data is None:
                abort(500, message="error occured during S3 file modification")
            else:
                if response_data.get("HTTPStatusCode") == 200:
                    book.mime_type = file_type.mime
                    try:
                        db.session.add(book)
                        db.session.commit()
                    except IntegrityError:
                        abort(409, message="error, database constraint violation occured")      
                    except SQLAlchemyError:
                        abort(500, message="error occured during tag insertion")

                    return {"code": 204, "message": "file modified"}
                else:
                    abort(500, message="error occurred during S3 file modification")
        else:
            # roll back aws ?
            abort(404, message="book not found")



@blp.route("/books")
class BookList(MethodView):
    @jwt_required()
    @blp.arguments(BookSearchQueryArgs, location="query")
    @blp.response(200, BookSchema(many=True))
    @blp.paginate(CursorPage)
    def get(self, search_values):
        """list multiple books"""
        title = search_values.get("title")
        release_year = search_values.get("release_year")
        sort = search_values.get("sort")
        order = search_values.get("order")

        result = BookModel.query            

        if title:
            result = result.filter(BookModel.title.contains(search_values.get("title")))        # TODO: simplify by not calling .get() again ??? (also in other files)
        if release_year:
            result = result.filter(BookModel.release_year.contains(search_values.get("release_year")))

        if sort in ["release_year", "title"] and order in ["asc", "desc"]:
            if order == "asc":
                result = result.order_by(sql.asc(sort))
            else: 
                result = result.order_by(sql.desc(sort))

        return result

    
    @jwt_required(fresh=True) 
    @blp.arguments(PlainBookSchema, location="form")
    @blp.arguments(MultipartFileSchema, location="files")
    @blp.response(201, BookSchema, description="created - book created")
    def post(self, book_data, files): 
        """add book"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

        # https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html

        # TODO: check maximum file size  X
        # TODO: Set a filename length limit. Restrict the allowed characters if possible
        # TODO: Change the filename to something generated by the application
        # TODO: Set a filename length limit. Restrict the allowed characters if possible
        # TODO: Validate the file type, don't trust the Content-Type header as it can be spoofed X

        book_file = files["file"]                       # <class 'werkzeug.datastructures.FileStorage'>

        '''check file size'''
        book_file.seek(0,2)
        if book_file.tell() > app.config["MAX_FILE_SIZE"]:
            abort(413, message="error, file too large")
        book_file.seek(0,0)
        
        '''check content type'''
        content_type = book_file.headers.get('Content-Type')

        if not content_type:
            abort(400, message="error, Content-Type header required")

        file_type = filetype.guess(book_file.read())
        book_file.seek(0)

        if file_type:
            if file_type.mime in app.config["FILE_FORMATS"]:
                if file_type.mime != content_type:
                    abort(422, message="error, inferred file type differs from Content-Header")
            else:
                abort(415, message="error, unsupported file type")
        else:
            abort(422, message="error, file type indeterminate")

        '''compress file'''
        book_file = gzip.compress(book_file.read())

        '''get MD5'''
        book_file_md5 = hashlib.md5(book_file).hexdigest()

        '''upload file'''
        bucket_url = app.config["AWS_S3_BUCKET_URL"]
        key = lid.get_link_id()
        
        response = s3.put_object(
            Bucket = "alexandria-api",
            Key = key,
            Body = book_file,
            ContentType = content_type
        )

        if response.get('ETag') and response.get('ETag') == '"' + book_file_md5 + '"':
            object_url = bucket_url + "/" + key

            '''add DB entry'''
            book_data["link_id"] = lid.get_link_id()
            book_data["file_url"] = object_url
            book_data["added_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            book_data["mime_type"] = file_type.mime
            book = BookModel(**book_data)

            # TODO: remove file when DB fails
            try:
                db.session.add(book)
                db.session.commit()
            except IntegrityError:
                abort(409, message="error, database constraint violation occured")
            except SQLAlchemyError:
                abort(500, message="error occured during book insertion")
        
            return book

        else:
            # TODO: delete file
            abort(500, message="error, file corruption occured during S3 upload")


@blp.route("/book/<string:book_id>/tag/<string:tag_id>")
class BookTags(MethodView):
    @jwt_required(fresh=True)
    @blp.response(201, BookSchema, description="created - book tag relation created")
    @blp.alt_response(404, description="book not found")
    @blp.alt_response(404, description="tag not found")
    def post(self, tag_id, book_id):
        """create relation between book and tag"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

        book = BookModel.query.filter_by(link_id = book_id).first()
        tag = TagModel.query.filter_by(link_id = tag_id).first()    
    
        if not book:
            abort(404, message="book not found")
        elif not tag:
            abort(404, message="tag not found")
        else:                                            # Todo: check efficiency
            book.tags.append(tag) 
            try:
                db.session.add(book)
                db.session.commit()
            except SQLAlchemyError:
                abort(500, message="an error occurred while creating book tag relation")
        
        return book

    @jwt_required(fresh=True)
    @blp.response(202, description="accepted - book tag relation deleted")
    @blp.alt_response(404, description="book not found")
    @blp.alt_response(404, description="tag not found")
    @blp.alt_response(404, description="no relation found for book and tag")
    def delete(self, tag_id, book_id):
        """delete relation between book and tag"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

        book = BookModel.query.filter_by(link_id = book_id).first()
        tag = TagModel.query.filter_by(link_id = tag_id).first()    
    
        if not book:
            abort(404, message="book not found")
        elif not tag:
            abort(404, message="tag not found")
        else:
            if tag not in book.tags:
                abort(404, message="no relation found for book and tag")
            else:
                book.tags.remove(tag)
                try:
                    db.session.add(book)
                    db.session.commit()
                except SQLAlchemyError:
                    abort(500, message="an error occurred while deleting book tag relation")

        return {"code": 202, "message": "book tag relation deleted"}
    

