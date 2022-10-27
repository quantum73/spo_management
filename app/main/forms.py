from enum import Enum

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import validators, StringField, FloatField, SubmitField, SelectField, IntegerField, FileField

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


class InputJSONForm(FlaskForm):
    from_json = FileField(
        'Заполнить',
        validators=[validators.Optional(), FileAllowed(['json'], 'JSON only!')],
        render_kw={
            'accept': 'application/JSON',
            'class': 'from-json-field',
        },
    )


class ParametersForm(InputJSONForm, FlaskForm):
    scene = SelectField(
        'Тип сцены:',
        choices=[(i.name, i.value) for i in SceneTypes],
        default=SceneTypes.oka.name,
        validators=[validators.DataRequired()],
    )
    title = StringField('Название:', validators=[validators.DataRequired(), validators.Length(min=3, max=128)])
    sample_count = IntegerField(
        'Количество сэмплов:',
        default=DEFAULT_SAMPLES_COUNT,
        validators=[validators.DataRequired(), validators.NumberRange(min=1)],
    )
    trajectory_type = SelectField(
        'Тип траектории:',
        choices=[(i.name, i.value) for i in Trajectory],
        default=Trajectory.glissade.name,
        validators=[validators.DataRequired()],
    )

    # glissade
    d_start = FloatField('D старт:', validators=[validators.Optional()])
    d_finish = FloatField('D финиш:', validators=[validators.Optional()])
    h_start = FloatField('H старт:', validators=[validators.Optional()])
    h_finish = FloatField('H финиш:', validators=[validators.Optional()])
    start_x_target = FloatField('X старт (м):', validators=[validators.Optional()])
    start_y_target = FloatField('Y старт (м):', validators=[validators.Optional()])
    start_z_target = FloatField('Z старт (м):', default=DEFAULT_Z, validators=[validators.Optional()])
    finish_x_target = FloatField('X финиш (м):', validators=[validators.Optional()])
    finish_y_target = FloatField('Y финиш (м):', validators=[validators.Optional()])
    finish_z_target = FloatField('Z финиш (м):', default=DEFAULT_Z, validators=[validators.Optional()])

    # ellipse
    h_min = FloatField('H макс. (м):', validators=[validators.Optional()])
    h_max = FloatField('H мин. (м):', validators=[validators.Optional()])
    r_x = FloatField('Rx (м):', validators=[validators.Optional()])
    r_y = FloatField('Ry (м):', validators=[validators.Optional()])
    r_z = FloatField('Rz (м):', default=DEFAULT_Z, validators=[validators.Optional()])
    x_target = FloatField('X (м):', validators=[validators.Optional()])
    y_target = FloatField('Y (м):', validators=[validators.Optional()])
    z_target = FloatField('Z (м):', default=DEFAULT_Z, validators=[validators.Optional()])

    # sensor
    sensor_name = StringField('Название:', validators=[validators.DataRequired(), validators.Length(min=3, max=64)])
    sensor_type = SelectField(
        'Тип сенсора:',
        choices=[(s.name, s.value) for s in SensorTypes],
        default=SensorTypes.IR.name,
        validators=[validators.DataRequired()],
    )
    resolution_x = IntegerField('X:', validators=[validators.DataRequired(), validators.NumberRange(min=1)])
    resolution_y = IntegerField('Y:', validators=[validators.DataRequired(), validators.NumberRange(min=1)])
    size_x = IntegerField('X:', validators=[validators.DataRequired(), validators.NumberRange(min=1)])
    size_y = IntegerField('Y:', validators=[validators.DataRequired(), validators.NumberRange(min=1)])
    field_view = IntegerField('Поле зрения (°):', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    host = StringField('Хост:', default="10.24.50.4", validators=[validators.DataRequired(), validators.IPAddress()])
    port = IntegerField('Порт:', default=4545,
                        validators=[validators.DataRequired(), validators.NumberRange(min=1000, max=9999)])
    clear_sensor = SubmitField(
        'Очистить',
        validators=[validators.Optional()],
        render_kw={
            'class': 'btn btn-danger btn-md clear-sensor-btn',
            'type': 'button',
        },
    )

    frequency = FloatField(
        'Частота кадров (Герц):',
        default=DEFAULT_FREQUENCY,
        validators=[validators.DataRequired(), validators.NumberRange(min=1)],
    )
    velocity = FloatField(
        'Скорость (м/с):',
        default=DEFAULT_VELOCITY,
        validators=[validators.DataRequired(), validators.NumberRange(min=1)],
    )

    submit = SubmitField(
        'Запуск',
        render_kw={
            "id": "go-btn",
            "class": "btn btn-info",
        },
    )
