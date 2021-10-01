from flask_wtf import Form 
from wtforms import StringField
from wtforms.validators import DataRequired

class To_From_Form(Form):
    from_text=StringField('from_text',validators=[DataRequired()])
    to_text=StringField('to_text',validators=[DataRequired()]) 
