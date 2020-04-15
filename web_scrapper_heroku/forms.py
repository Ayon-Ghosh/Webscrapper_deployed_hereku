from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class SearchForm(FlaskForm):
	item = StringField("Item", validators =[DataRequired(), Length(min=1, max=50)])
	model = StringField("Model")
	color = StringField("Color")
	submit = SubmitField('Search')
