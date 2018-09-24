from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, NumberRange
from flask_codemirror.fields import CodeMirrorField


class StrategyForm(FlaskForm):
    name = StringField('Please input your strategy name:', validators=[DataRequired()])
    start_date = DateField('From', format='%Y-%m-%d')
    end_date = DateField('To', format='%Y-%m-%d')
    stock = IntegerField('Stock ¥', validators=[NumberRange(min=1), DataRequired()])
    source_code = CodeMirrorField(language='python', config={'lineNumbers' : 'true'}) 
    save_strategy = BooleanField('Save my strategy')
    submit = SubmitField('Submit')

	