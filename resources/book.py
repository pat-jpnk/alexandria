from flask import current_app as app
from flask.views import MethodView
from flask_smorest import * #Blueprint, abort
from flask_smorest.fields import Upload
from flask_jwt_extended import jwt_required
from schemas import BookSchema, BookUpdateSchema, PlainBookSchema, MultipartFileSchema, BookSearchQueryArgs
from werkzeug.utils import secure_filename
from models import BookModel, TagModel
from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import sqlalchemy.sql as sql
import link_id as lid
import datetime 

from S3 import s3
import filetype

# todo: replace aws
import gzip

#temporary
import os.path
from flask import send_from_directory


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

    # TODO: delete file when deleting book
    @jwt_required(fresh=True)
    @blp.response(202, description="accepted - book deleted")
    @blp.alt_response(404, description="book not found")
    def delete(self, book_id):
        """delete book"""
        book = BookModel.query.filter_by(link_id = book_id).first()

        if book:
            try:
                db.session.delete(book)
                db.session.commit()
            except SQLAlchemyError:
                abort(500, message="error occurred during book deletion")
        else:
            abort(404, message="book not found")

        return {"code": 200,"message": "book deleted successfully"}
    
    @jwt_required(fresh=True)
    @blp.arguments(BookUpdateSchema)
    @blp.response(204, BookSchema,  description="success, no content - tag modified")
    @blp.alt_response(409, description="database constraint violation")
    @blp.alt_response(404, description="book not found")
    def put(self, book_data, book_id):      # book data goes first, book_data is extra parameter added by smorest arguments decorator        
        """modify book"""
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

# TODO: COMPLETE
@blp.route("/book/<string:book_id>/file")
class BookFile(MethodView):
    #@jwt_required()
    @blp.response(200)
    @blp.alt_response(404, description="book not found")
    def get(self, book_id):
        """get book file"""
        #file_url = BookModel.query.filter_by(link_id = book_id).first().file_url

        #if not file_url:
        #    abort(404, message="book not found")  
        
        '''
        with open('book', 'wb') as book_file:
            s3.download_fileobj("alexandria-api", "6XHKJCSGCRV32RHQC4RG", book_file)
            book_file.flush()

        book_file.read()
        '''

        book_file = s3.get_object(Bucket='alexandria-api', Key='CCT68DK4C9H3ERK46GSG')['Body'].read()
        book_file = gzip.decompress(book_file)


#        exit()

        from flask import Response

        response = Response(book_file, mimetype="application/pdf")
        response.headers.set("Content-Disposition", "attachment", filename="book.pdf")
        return response

        #response = make_response(book_file)
        #response.headers.set('Content-Type', 'application/pdf')  # use db var
        #response.headers.set('Content-Disposition', 'attachment', filename="file.pdf") # change

        #return response

        # decompress

        '''
        with gzip.open(file_url, "rb") as comp_file:
            raw_file = comp_file.read()
            print(type(raw_file))
            exit()
        '''
        # .gz
        #return send_from_directory("/home/patrick/Programming/alexandria/tempfiles","bwl1zh848g6a1.jpg ", as_attachment=True)

    @jwt_required()
    @blp.response(204, BookSchema,  description="success, no content - tag modified")

    @jwt_required()
    @blp.response(204)
    #@blp.alt_response()
    @blp.arguments(MultipartFileSchema, location="files")
    def put(self, book_id):
        pass # TODO: update book file



@blp.route("/books")
class BookList(MethodView):
    #@jwt_required()
    @blp.arguments(BookSearchQueryArgs, location="query")
    @blp.response(200, BookSchema(many=True))
    @blp.paginate(CursorPage)
    def get(self, search_values):
        """list multiple books"""
        #return BookModel.query.all()
        print(search_values)            # TODO: remove

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

    
    #@jwt_required(fresh=True) 
    @blp.arguments(PlainBookSchema, location="form")
    @blp.arguments(MultipartFileSchema, location="files")
    @blp.response(201, BookSchema, description="created - book created")
    def post(self, book_data, files): 
        
        book_file = files["file"]                       # <class 'werkzeug.datastructures.FileStorage'>

        '''check file size'''
        book_file.seek(0,2)
        print("len: ", book_file.tell()) # in bytes
        book_file.seek(0,0)
        
        book_file.seek(0,2)
        if book_file.tell() > app.config["MAX_FILE_SIZE"]:
            print("ERROR 2")
            exit()
        

        book_file.seek(0,0)
        

        '''check content type'''
        content_type = book_file.headers.get('Content-Type')

        if content_type:
            pass
        else:
            pass

        file_type = filetype.guess(book_file.read())
        #book_file.seek(0)

        if file_type:
            if file_type.mime in app.config["FILE_FORMATS"]:
                if file_type.mime == content_type:
                    pass
                else:
                    print("ERROR 3")
                    exit()
            else:
                print("ERROR 4")
                exit()
        else:
            print("ERROR 5")
            exit()


        '''compress file'''
        book_file = gzip.compress(book_file.read())


        '''get MD5'''
        import hashlib
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
            book = BookModel(**book_data)

            print("BOOK: ", book_data)

            try:
                db.session.add(book)
                db.session.commit()
            except IntegrityError:
                abort(409, message="error, database constraint violation occured")
            except SQLAlchemyError:
                abort(500, message="error occured during book insertion")
        
            return book



        else:
            print("etag: ", type(response.get('ETag')))
            print("md5: ", type(book_file_md5))
            print("ERROR 1")
            exit()
        '''        

        book_data["link_id"] = lid.get_link_id()
        book_data["file_url"] = "dddddddd" #object_url
        book_data["added_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        book = BookModel(**book_data)

        print("BOOK: ", book_data)

        try:
            db.session.add(book)
            db.session.commit()
        except IntegrityError:
            abort(409, message="error, database constraint violation occured")
        except SQLAlchemyError:
            abort(500, message="error occured during book insertion")
        
        return book
        '''



        # ----------------------------------------------------------------------------------------------------------

        # files

        #from app import create_app
        #app = create_app()

        # TODO: decide on solution for duplicate file name (do not use filename, use link_id)

        # https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html

        # TODO: check maximum file size  X
        # TODO: Set a filename length limit. Restrict the allowed characters if possible
        # TODO: Change the filename to something generated by the application
        # TODO: Set a filename length limit. Restrict the allowed characters if possible
        # TODO: Validate the file type, don't trust the Content-Type header as it can be spoofed X

        # https://s3-REGION-.amazonaws.com/BUCKET-NAME/KEY

        # eu-central-1
        # alexandria-api

        # https://s3-eu-central-1.amazonaws.com/alexandria-api/    app.config["AWS_S3_BUCKET_URL"]


        """
        - compress before upload, no S3 feature
        - use book_file.read() to get byte stream of <class 'werkzeug.datastructures.FileStorage'> for upload without saving
        
        - somehow compresss bytestream instead of file

        - upload bytes using s3 put_object 

        https://www.learnaws.org/2022/08/22/boto3-s3-upload_file-vs-put-object/
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html
        https://saturncloud.io/blog/flask-upload-image-to-s3-without-saving-to-local-file-system/


        """



        """create book"""
        #print(files["file"].filename)
        
        ###book_file = files["file"]                       # <class 'werkzeug.datastructures.FileStorage'>
        
       # book_file.read()
       # book_file.seek(0)

        #print(type(book_file))          

        ###print("name: ", book_file.filename)

        # book_file.headers.get('Content-Type') == 'application/pdf'

        ###print("headers: ", book_file.headers)

        # https://pocoo-libs.narkive.com/pMsdZlrr/filestorage-content-length-always-zero

    

        '''get file size'''
        ###book_file.seek(0,2)
        ###print("len: ", book_file.tell()) # in bytes
        ###book_file.seek(0,0)
        
        '''get content type'''
        ###content_type = book_file.headers.get('Content-Type')

        
        ###if content_type:
            ###if content_type not in app.config["FILE_FORMATS"]:  # 'application/pdf':
                ###pass
        ###else:
            ###print('NOOOOOO') # content type header not found

    


      



    

      # --------------------------------------------------------------------------------------------

        '''

        book_data["link_id"] = lid.get_link_id()
        book_data["file_url"] = comp_book_path # todo change
        book_data["added_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        book = BookModel(**book_data)

        try:
            db.session.add(book)
            db.session.commit()
        except IntegrityError:
            abort(409, message="error, database constraint violation occured")
        except SQLAlchemyError:
            abort(500, message="error occured during book insertion")
        
        return book
        '''

@blp.route("/book/<string:book_id>/tag/<string:tag_id>")
class BookTags(MethodView):
    @jwt_required(fresh=True)
    @blp.response(201, BookSchema, description="created - book tag relation created")
    @blp.alt_response(404, description="book not found")
    @blp.alt_response(404, description="tag not found")
    def post(self, tag_id, book_id):
        """create relation between book and tag"""
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
                abort(500, message="an error occurred while adding tag")
        
        return book

    @jwt_required(fresh=True)
    @blp.response(202, description="accepted - book tag relation deleted")
    @blp.alt_response(404, description="book not found")
    @blp.alt_response(404, description="tag not found")
    @blp.alt_response(404, description="no relation found for book and tag")
    def delete(self, tag_id, book_id):
        """delete relation between book and tag"""
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
                    abort(500, message="an error occurred while adding tag")

        return {"message": "tag removed from book", "book": book, "tag": tag}
    

