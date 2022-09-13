import datetime
import json

from flask import render_template, redirect, url_for, jsonify
from flask_cors import cross_origin

from . import main
from .forms import ParametersForm, InputJSONForm


@main.route('/', methods=['GET', 'POST'])
@cross_origin()
def home():
    parameters_from = ParametersForm()
    if parameters_from.validate_on_submit():
        print(parameters_from.data)
        # TODO: Какая-то логика передачи данных на отрисовку
        return redirect(url_for('main.results'))

    return render_template("main/home.html", parameters_from=parameters_from), 200


@main.route('/check-json/', methods=['GET', 'POST'])
def check_json():
    json_form = InputJSONForm()
    if json_form.validate():
        data = json.load(json_form.from_json.data)
        return jsonify(data), 200
    return jsonify(json_form.errors), 400


@main.route('/results/', methods=['GET'])
def results():
    now = datetime.datetime.now()
    str_now = now.strftime("%H:%M %d.%m.%Y")
    return render_template("main/results.html", now_date=str_now), 200
