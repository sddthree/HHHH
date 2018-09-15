from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from flask_codemirror.fields import CodeMirrorField


class StrategyForm(FlaskForm):
    name = StringField('Please input your strategy name:', validators=[DataRequired()])
    source_code = CodeMirrorField(language='python', config={'lineNumbers' : 'true'}) 
    save_strategy = BooleanField('Save my strategy')
    submit = SubmitField('Submit')

	