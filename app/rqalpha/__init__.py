from flask import Blueprint

rqalpha = Blueprint('rqalpha', __name__)

from . import views