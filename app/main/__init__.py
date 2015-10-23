from flask import Blueprint

main = Blueprint('main',__name__)

#from . import views
from . import downimgViews,jobViews,scriptViews,serviceViews,testSuitViews,resumeViews,reportViews,analysisViews,loginViews
