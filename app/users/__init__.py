from flask import Blueprint
from flask_cors import CORS, cross_origin

user_api = Blueprint('user_api', __name__)

from . import views
