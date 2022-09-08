from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length


class ParametersForm(FlaskForm):
    title_name = StringField('Название:', validators=[DataRequired(), Length(min=3, max=128)])
    x_value = FloatField('X:', validators=[DataRequired()])
    y_value = FloatField('Y:', validators=[DataRequired()])
    z_value = FloatField('Z:', validators=[DataRequired()])
    submit = SubmitField('Создать')
