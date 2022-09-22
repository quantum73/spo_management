import datetime
import json
import os

import requests
from flask import render_template, redirect, url_for, jsonify, current_app, send_from_directory, alert
from flask_cors import cross_origin

from . import main
from .forms import ParametersForm, InputJSONForm


@main.route('/', methods=['GET', 'POST'])
@cross_origin()
def home():
    parameters_from = ParametersForm()
    if parameters_from.validate_on_submit():
        full_data = parameters_from.data
        full_data.pop("sensors")

        for sensor in parameters_from.sensors.data:
            full_data.update(sensor)
            host = sensor.get("host")
            port = sensor.get("port")
            response = requests.post(
                "http://{}:{}/run/".format(host, port),
                json=full_data,
            )
            if response.status_code == 200:
                # TODO: Получение URL для скачивания выборки
                print(response.json())
            else:
                alert("Непредвиденная ошибка. Введите данные заново.")
                break
        else:
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


@main.route('/favicon.ico')
def favicon():
    favicon_dir = os.path.join(current_app.config.get("STATIC_FOLDER"), "icons")
    return send_from_directory(favicon_dir, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
