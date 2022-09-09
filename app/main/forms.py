from enum import Enum

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, SelectField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, IPAddress

DEFAULT_Z = 10
DEFAULT_SAMPLES_COUNT = 10
DEFAULT_FREQUENCY = 25
DEFAULT_VELOCITY = 100


class SceneTypes(Enum):
    oka = "ОКА"
    ural = "Урал"
    kaspiy = "Каспий"


class SensorTypes(Enum):
    IR = "IR"
    TV = "TV"
    RL = "RL"
    JSON = "JSON"


class Trajectory(Enum):
    glissade = "Глиссада"
    ellipse = "Эллипс"


class SensorForm(FlaskForm):
    sensor_name = StringField('Название:', validators=[DataRequired(), Length(min=3, max=64)])
    sensor_type = SelectField(
        'Тип сенсора:',
        choices=[(s.name, s.value) for s in SensorTypes],
        default=SensorTypes.IR.name,
        validators=[DataRequired()],
    )
    resolution_x = IntegerField('X:', validators=[DataRequired(), NumberRange(min=64)])
    resolution_y = IntegerField('Y:', validators=[DataRequired(), NumberRange(min=64)])
    size_x = IntegerField('X:', validators=[DataRequired(), NumberRange(min=1)])
    size_y = IntegerField('Y:', validators=[DataRequired(), NumberRange(min=1)])
    field_view = IntegerField('Поле зрения (°):', validators=[DataRequired(), NumberRange(min=1)])
    host = StringField('Хост:', validators=[DataRequired(), IPAddress()])
    port = IntegerField('Порт:', validators=[DataRequired(), NumberRange(min=1000, max=9999)])


class ParametersForm(FlaskForm):
    scene = SelectField(
        'Тип сцены:',
        choices=[(i.name, i.value) for i in SceneTypes],
        default=SceneTypes.oka.name,
        validators=[DataRequired()],
    )
    title = StringField('Название:', validators=[DataRequired(), Length(min=3, max=128)])
    sample_count = IntegerField(
        'Количество сэмплов:',
        default=DEFAULT_SAMPLES_COUNT,
        validators=[DataRequired(), NumberRange(min=1)],
    )
    trajectory_type = SelectField(
        'Тип траектории:',
        choices=[(i.name, i.value) for i in Trajectory],
        default=Trajectory.glissade.name,
        validators=[DataRequired()],
    )

    # glissade
    d_start = FloatField('D старт:', validators=[Optional(), NumberRange(min=0)])
    d_finish = FloatField('D финиш:', validators=[Optional(), NumberRange(min=0)])
    h_start = FloatField('H старт:', validators=[Optional(), NumberRange(min=0)])
    h_finish = FloatField('H финиш:', validators=[Optional(), NumberRange(min=0)])
    start_x_target = FloatField('X старт (м):', validators=[Optional(), NumberRange(min=0)])
    start_y_target = FloatField('Y старт (м):', validators=[Optional(), NumberRange(min=0)])
    start_z_target = FloatField('Z старт (м):', default=DEFAULT_Z, validators=[Optional(), NumberRange(min=0)])
    finish_x_target = FloatField('X финиш (м):', validators=[Optional(), NumberRange(min=0)])
    finish_y_target = FloatField('Y финиш (м):', validators=[Optional(), NumberRange(min=0)])
    finish_z_target = FloatField('Z финиш (м):', default=DEFAULT_Z, validators=[Optional(), NumberRange(min=0)])

    # ellipse
    h_min = FloatField('H макс. (м):', validators=[Optional(), NumberRange(min=0)])
    h_max = FloatField('H мин. (м):', validators=[Optional(), NumberRange(min=0)])
    r_x = FloatField('Rx (м):', validators=[Optional(), NumberRange(min=0)])
    r_y = FloatField('Ry (м):', validators=[Optional(), NumberRange(min=0)])
    r_z = FloatField('Rz (м):', default=DEFAULT_Z, validators=[Optional(), NumberRange(min=0)])
    x_target = FloatField('X (м):', validators=[Optional(), NumberRange(min=0)])
    y_target = FloatField('Y (м):', validators=[Optional(), NumberRange(min=0)])
    z_target = FloatField('Z (м):', default=DEFAULT_Z, validators=[Optional(), NumberRange(min=0)])

    # sensors
    sensors = FieldList(
        FormField(SensorForm),
        min_entries=1,
        max_entries=5,
        # label="Сенсоры:",
        validators=[DataRequired()],
    )

    frequency = FloatField(
        'Частота кадров (Герц):',
        default=DEFAULT_FREQUENCY,
        validators=[DataRequired(), NumberRange(min=1)],
    )
    velocity = FloatField(
        'Скорость (м/с):',
        default=DEFAULT_VELOCITY,
        validators=[DataRequired(), NumberRange(min=1)],
    )

    submit = SubmitField(
        'Запуск',
        render_kw={'class': 'btn btn-primary btn-md'},
    )