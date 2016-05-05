from flask import Blueprint

main = Blueprint('main',__name__)

from . import jobViews,scriptViews,serviceViews,resumeViews,reportViews,analysisViews,loginViews
