from flask.views import MethodView
from flask_smorest import * #Blueprint, abort
from flask_smorest.fields import Upload
from flask_jwt_extended import jwt_required
from schemas import BookSchema, BookUpdateSchema, PlainBookSchema, MultipartFileSchema, BookSearchQueryArgs #BooktagSchema
from werkzeug.utils import secure_filename
from models import BookModel, TagModel
from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import sqlalchemy.sql as sql
import link_id as lid

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
    
    #@jwt_required(fresh=True)
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
    @jwt_required()
    @blp.response(200)
    @blp.alt_response(404, description="book not found")
    def get(self, book_id):
        """get book file"""
        file_url = BookModel.query.filter_by(link_id = book_id).first().file_url

        if not file_url:
            abort(404, message="book not found")  

        # decompress

        with gzip.open(file_url, "rb") as comp_file:
            raw_file = comp_file.read()
            print(type(raw_file))
            exit()
        
        # .gz
        return send_from_directory("/home/patrick/Programming/alexandria/tempfiles","bwl1zh848g6a1.jpg ", as_attachment=True)


@blp.route("/books")
class BookList(MethodView):
   # @jwt_required() RE ENABLE
    #@blp.arguments(Book)
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

    
    #@blp.arguments(PlainBookSchema)
    #@jwt_required(fresh=True) RE ENABLE
    @blp.arguments(PlainBookSchema, location="form")
    @blp.arguments(MultipartFileSchema, location="files")
    @blp.response(201, BookSchema, description="created - book created")
    def post(self, book_data, files): # files

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
        print(files["file"].filename)
        book_file = files["file"]                       # <class 'werkzeug.datastructures.FileStorage'>
        
       # book_file.read()
       # book_file.seek(0)

        #print(type(book_file))          

        print("name: ", book_file.filename)

        # book_file.headers.get('Content-Type') == 'application/pdf'

        print("headers: ", book_file.headers)

        # https://pocoo-libs.narkive.com/pMsdZlrr/filestorage-content-length-always-zero

    

        '''get file size'''
        book_file.seek(0,2)
        print("len: ", book_file.tell()) # in bytes
        book_file.seek(0,0)
        
        '''get content type'''
        content_type = book_file.headers.get('Coxntent-Type')

        if content_type:
            if content_type != 'application/pdf':
                pass
        else:
            print('NOOOOOO') # content type header not found


        '''
        app.config["FILE_FORMATS"] = ["application/pdf"]
        app.config["MAX_FILE_SIZE"] = 300000000         

        
        '''    

        '''compress bytes'''

        '''

        print("")

        #print("uncon: ", book_file.read().hex())       
        print("uncon len: ", len(book_file.read().hex()))        


        print("read type: ", type(book_file.read()))        # read type:  <class 'bytes'>
        print("read: ", book_file.read())
        print("read hex: ", book_file.read().hex())
        con = gzip.compress(book_file.read())               # com type:  <class 'bytes'>
        
        print("con type: ", type(con))
        print("con len: ", len(con))

        print("con: ", con)
        print("con hex: ", con.hex())        

        print("print con after .hex(): ", con)


        uu = gzip.decompress(con)
        print("uu type: ", type(uu))
        '''

        print("")

        print("uncompressed len hex: ", len(book_file.read().hex()))

        book_file.seek(0,0)

        compp = gzip.compress(book_file.read())
        
        book_file.seek(0,0)

        print("compressed len hex: ", len(compp.hex()))

        u_compp = gzip.decompress(compp)

        print("uncompressed len hex: ", len(u_compp.hex()))


        

        exit()

        base_dir = "/home/patrick/Programming/alexandria/tempfiles"   # replace with variable maybe
        book_path = os.path.join(base_dir, secure_filename(book_file.filename))
        comp_book_path = book_path + '.gz'
        book_file.save(book_path)

        with open(book_path, 'rb') as raw_file, gzip.open(comp_book_path, 'wb') as comp_file:
            comp_file.writelines(raw_file)

        #print(book_data)

        if os.path.exists(book_path):
            os.remove(book_path)
            pass
        else:
            pass
        
        '''
        
        uncompressed: 71.1 kB
        compressed: 67.7 kB
        
        -> jpeg, already pretty compressed, have to check pdf

        '''

        book_data["link_id"] = lid.get_link_id()
        book_data["file_url"] = comp_book_path
        book = BookModel(**book_data)

        try:
            db.session.add(book)
            db.session.commit()
        except IntegrityError:
            abort(409, message="error, database constraint violation occured")
        except SQLAlchemyError:
            abort(500, message="error occured during book insertion")
        
        return book


@blp.route("/book/<string:book_id>/tag/<string:tag_id>")
class BookTags(MethodView):
    #@jwt_required(fresh=True)
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
    

