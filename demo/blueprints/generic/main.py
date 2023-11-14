from flask import request,current_app
from utils import file
from blueprints.generic import generic_bp


@generic_bp.route('/hello',methods=['get'])
def hello():
    return "SUCCESS"

@generic_bp.route('/upload', methods=['post'])
def uploads():
    upload_file = request.files['file']
    return file.upload(upload_file, app=current_app)


@generic_bp.route('/compress_image', methods=['post'])
def compress_image():
    upload_file = request.files['file']
    return file.compress_image(upload_file, app=current_app, format_='PNG')
