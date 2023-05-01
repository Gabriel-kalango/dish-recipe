import os
import re
from werkzeug.datastructures import FileStorage
from flask_uploads import IMAGES,UploadSet
from typing import Union
IMAGE_SET=UploadSet("images",IMAGES)



def save_image(image:FileStorage,folder:str=None,name:str=None)->str:
    """ takes a filestorage and saves it to a folder"""
    return IMAGE_SET.save(image,folder,name)

def get_path(filename:str=None,folder:str=None)->str:
    """takes image name and folder and gets the path to the image """
    return IMAGE_SET.path(filename,folder)


def find_image_format(filename:str,folder:str=None)->Union[str,None]:
    """takes a filename and return an image on any of the accepted format"""
    for _format in IMAGES:
        image=f"{filename}.{_format}"
        image_path=IMAGE_SET.path(filename=image,folder=folder)
        if os.path.isfile(image_path):
            return image_path
    return None


def retrieve_filename(file:Union[str,FileStorage])->str:
    """if the file is a file storage return the file name or if it is just a filename return it """
    if isinstance(file,FileStorage):
        return file.filename
    return file

def is_filename_safe(file:Union[str,FileStorage])->bool:
    """checks our regex and return the filename matches or not """
    filename=retrieve_filename(file)
    allowed_format="|".join(IMAGES)
    regex=f"^[A-Za-z0-9][A-Za-z0-9()_\-\.]*\.({allowed_format})$"
    return re.match(regex,filename) is not None

def get_basename(file:Union[str,FileStorage])->str:
    """ get the name of the image"""
    filename=retrieve_filename(file)
    return os.path.split(filename)[1]


def get_extension(file:Union[str,FileStorage])->str:
    """get the extension of the image"""
    filename=retrieve_filename(file)
    return os.path.splitext(filename)[1]