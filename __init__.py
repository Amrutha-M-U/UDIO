from flask import Flask
from app import configuration
from app.model import dbSetUp

application=Flask(__name__)
application.config.from_object(configuration)
dbSetUp()
from app import views
from app.sender import sender_views
from app import dashboard_views
from app import api
