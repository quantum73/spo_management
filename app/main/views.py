import json
import os
import uuid

import requests
from flask import render_template, redirect, url_for, jsonify, current_app, send_from_directory
from flask_cors import cross_origin
from sqlalchemy import desc

from . import main
from .forms import ParametersForm, InputJSONForm
from .. import db
from ..models import Result


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
            try:
                response = requests.post(
                    "http://{}:{}/run/".format(host, port),
                    json=full_data,
                    timeout=1,
                )
            except Exception as e:
                is_ok_flag = False
                result_content = e.__class__.__name__
            else:
                if response.status_code == 200:
                    # TODO: Получение URL для скачивания выборки
                    data = response.json()
                    is_ok_flag = True
                    result_content = "http://{}:{}/download/{}/".format(host, port, uuid.uuid4())
                    # result_content = data.get("download_url")
                else:
                    is_ok_flag = False
                    result_content = f"Error: {response.status_code}"

            result = Result(
                title=full_data.get("title"),
                host=f"{host}:{port}",
                is_ok=is_ok_flag,
                content=result_content,
            )
            db.session.add(result)
            db.session.commit()
        else:
            return redirect(url_for('main.get_results'))

    return render_template("main/home.html", parameters_from=parameters_from), 200


@main.route('/check-json/', methods=['GET', 'POST'])
def check_json():
    json_form = InputJSONForm()
    if json_form.validate():
        data = json.load(json_form.from_json.data)
        return jsonify(data), 200
    return jsonify(json_form.errors), 400


@main.route('/results/', methods=['GET'])
def get_results():
    results = Result.query.order_by(desc(Result.created_at)).all()
    return render_template("main/results.html", results=results), 200


@main.route('/favicon.ico')
def favicon():
    favicon_dir = os.path.join(current_app.config.get("STATIC_FOLDER"), "icons")
    return send_from_directory(favicon_dir, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
