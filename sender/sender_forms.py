from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
SECRET_KEY='dont wanna know this$'

#sender registration form

class RegForm(Form):
    name=StringField('name', validators=[DataRequired()])
    username=StringField('username',validators=[DataRequired()])
    password=StringField('password',validators=[DataRequired()])
    confirm=StringField('confirm',validators=[DataRequired()])

        
