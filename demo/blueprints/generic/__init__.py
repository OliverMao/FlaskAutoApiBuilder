# @FileName: __init__.py

from flask import Blueprint, request


generic_bp = Blueprint("generic", __name__)
from . import main