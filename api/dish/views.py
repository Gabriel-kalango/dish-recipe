from flask_restx import Resource,abort
from ..models import User,Dish
from ..schema import dish_create,dish_namespace,dish_view,ImageSchema
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask_socketio import emit
from flask import request,send_file
from ..libs import image_helper
from flask_uploads import UploadNotAllowed
import os
from mimetypes import guess_type
import traceback

@dish_namespace.route("")
class Recipes(Resource):
    #a user dishes created
    @dish_namespace.doc(security="jwt")
    @dish_namespace.marshal_list_with(dish_view)
    @dish_namespace.response(200,dish_view)
    @dish_namespace.response(404,"Not found")
    @jwt_required()
    def get(self):
        """dishes created by a particular user"""
        user_id=get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        dishes = Dish.query.filter(Dish.user_id==user_id).order_by(Dish.date_posted.desc()).paginate(page=page, per_page=per_page)
        print(dishes)
        return dishes.items, 200, {'X-Total-Count': dishes.total,"status":"success"}
        
    

        
    
        
    #posting your dish
    @dish_namespace.expect(dish_create)
    @dish_namespace.doc(security="jwt")
    @dish_namespace.response(201,"dish created successfully")
    @dish_namespace.response(400,"bad request")
    @jwt_required()
    def post(self):
        """creating your dish """
        user_id=get_jwt_identity()
        data=dish_namespace.payload
        name=data.get("name")
        instructions=data.get("instructions")   
        ingredients=data.get("ingredients")
        new_dish=Dish(name=name,instructions=instructions,ingredients=ingredients,user_id=user_id)
        
        new_dish.save()
        return {"status":"success","message":"dish uploaded successfully"},201

@dish_namespace.route("/<int:id>")
class GetUpdateDeleteDish(Resource):
    #get a particular dish
    @dish_namespace.marshal_with(dish_create,envelope="resource")
    @dish_namespace.response(200,dish_create)
    @dish_namespace.response(404,"Not found")
    def get(self,id):
        """get a particular dish"""
        dish=Dish.query.get_or_404(id)
    
        
        return  {"status":"success",
            "id": dish.id,
            "name": dish.name,
            "ingredients": dish.ingredients,
            "instructions": dish.instructions,
        }, 200
    #creating an endpoint to update dishes
    @jwt_required()
    @dish_namespace.doc(security="jwt")
    @dish_namespace.expect(dish_create)
    @dish_namespace.response(200,"dish updated successfully")
    @dish_namespace.response(404,"Not found")
    @dish_namespace.response(403,"forbidden")
    def put(self,id):
        """updating dishes"""
        user_id=get_jwt_identity()
        if Dish.query.filter(Dish.user_id==user_id).first():
            data=dish_namespace.payload
            dish=Dish.query.get(id)
            if dish:
                dish.name=data.get("name")
                dish.instructions=data.get("instructions")
                dish.ingredients=data.get("ingredients")
                dish.set_ingredients(dish.ingredients)
                dish.update()
                return {"status":"success","message":"dish has been updated"},200
            abort(404,message="this post doesnt exist",status="error")
        abort(403,message="you are not the owner of this account",status="error")

    #creating an endpoint to delete dish
    @dish_namespace.response(200,"delete successful")
    @dish_namespace.response(404,"Nor found")
    @dish_namespace.response(403,"forbidden")
    @dish_namespace.doc(security="jwt")
    @jwt_required()
    def delete(self,id):
        """delete a dish"""
        user_id=get_jwt_identity()
        if Dish.query.filter(Dish.user_id==user_id).first():
            dish=Dish.query.get_or_404(id)
            dish.delete()
            return {"status":"success","message":"dish deleted successfully"},200
        abort(403,message="you are not the owner of this account",status="error")
# creating an endpoint to handle the liking and disliking a dish
@dish_namespace.route("/likes/<int:id>")
class postlikes(Resource):
        @dish_namespace.response(200,"like/dislike was successful")
        @dish_namespace.response(404,"Not found")
        @dish_namespace.response(403,"Forbidden")
        @dish_namespace.doc(security="jwt")
        @jwt_required()
        def post(self,id):
            """liking and disliking a dish"""
            user_id=get_jwt_identity()
            user=User.query.get(user_id)
            dish=Dish.query.get_or_404(id)
            if user is not  None:
                if user not in dish.user_likes:
                    dish.user_likes.append(user)
                    dish.update()
                    
                else:
                    dish.user_likes.remove(user)
                    dish.update()
                updated_likes=len(dish.user_likes)
                emit('like', {'dish_id': dish.id, 'like_count': updated_likes}, broadcast=True , namespace=dish_namespace)

                return {"status":"success","number_of_likes":updated_likes},200

            abort(404,message="user doesnt exist",status="error")

@dish_namespace.route("/image/<id>")
class Imagee(Resource):
    @dish_namespace.doc(security="jwt")
    @dish_namespace.response(201,"image has been uploaded")
    @dish_namespace.response(400,"bad request")
    @dish_namespace.response(500,"Sever unavailable")
    @jwt_required()
    def put(self,id):
        """uploading images"""
        # a put method used to upload the image , the image path is then saved in the database while the image is saved in a folder (static/images)
        data=ImageSchema().load(request.files)
        user_id=get_jwt_identity()
        
        avatar_path=image_helper.find_image_format(data["image"].filename)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                abort(500,message="avatar deletion failed")
        try:
            dish=Dish.query.get_or_404(id)
            if dish.user_id!=user_id:
                abort(403,message="you are not authorized to make this change")
            image_path=image_helper.save_image(data["image"])
            file_path=image_helper.get_path(image_path)
            dish.dish_image_url=file_path
            dish.update()
            basename=image_helper.get_basename(image_path)
            return {"status":"success","message":f"{basename} has been uploaded"},201
        except UploadNotAllowed:
            extension=image_helper.get_extension(data["image"])
            return {"status":"error","message":f"this {extension} is not allowed"},400


@dish_namespace.route("/images/<id>")
class image(Resource):
# a get method for reading the images
    @dish_namespace.response(200,"image viewed successfully")
    @dish_namespace.response(404,"Not found")
    @dish_namespace.response(500,"Sever unavailable")
    def get(self,id):
        """reading of the images"""
        dish=Dish.query.get_or_404(id)
        image_path=dish.dish_image_url
        try:
            # get the current working directory
            current_dir = os.getcwd()


            
            
            
            file_path_=os.path.join(current_dir,image_path)
            absolute_path=os.path.abspath(file_path_)
            
        
            return send_file(absolute_path)

   

        except FileNotFoundError:
            abort(404,message=f"file not found ",status="error")

    @dish_namespace.doc(security="jwt")
    @dish_namespace.response(201,"image deletion successful")
    @dish_namespace.response(404,"Not found")
    @dish_namespace.response(500,"Sever unavailable")
    @jwt_required()
    def delete(self,filename):
        user_id=get_jwt_identity()
        folder=f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            abort(400,message=f"this {filename} is not supported",status="error")
        try:
            # get the current working directory
            current_dir = os.getcwd()



            file_path=image_helper.get_path(filename,folder=folder)
            file_path_=os.path.join(current_dir,file_path)
            absolute_path=os.path.abspath(file_path_)
        
            os.remove(absolute_path)
            return {"status":"success","message":"image deleted successfully"}

   

        except FileNotFoundError:
            abort(404,message=f"file with name {filename} not found ",status="error")
        
        except:
            traceback.print_exc()
            abort(500,message="image deletion failed",status="error")




