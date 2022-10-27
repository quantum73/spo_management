import json
import os
import socket
from multiprocessing import Process

from flask import render_template, redirect, url_for, jsonify, current_app, send_from_directory
from flask_cors import cross_origin
from sqlalchemy import desc

from manage import curr_app
from . import main
from .dataset_task import CreateDatasetTask, TaskResponse
from .forms import ParametersForm, InputJSONForm
from .. import db
from ..models import Result


def run_task(result_id: int, host: str, port: int, form_data: dict) -> None:
    try:
        runner = CreateDatasetTask(ip=host, port=port, params=form_data)
        res = runner.run()
    except socket.error as socket_err:
        print(">>> [SOCKET ERROR]: ", socket_err)
        res = TaskResponse()
        res.content = socket_err.__class__.__name__

    is_ok_flag = True if res.status == "OK" else False
    with curr_app.app_context():
        Result.query.filter_by(id=result_id).update(
            dict(is_ok=is_ok_flag, content=res.content)
        )
        db.session.commit()


@main.route('/', methods=['GET', 'POST'])
@cross_origin()
def home():
    parameters_from = ParametersForm()
    if parameters_from.validate_on_submit():
        form_data = parameters_from.data
        title = form_data.get("title")
        scene = form_data.get("scene").upper()
        host = form_data.get("host")
        port = form_data.get("port")
        result = Result(
            title="{0} [{1}]".format(title, scene),
            host=f"{host}:{port}",
            content="PROCESSING",
        )
        db.session.add(result)
        db.session.commit()

        func_kwargs = {
            "result_id": result.id,
            "host": host,
            "port": port,
            "form_data": form_data,
        }
        process = Process(target=run_task, kwargs=func_kwargs)
        process.daemon = True
        process.start()
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
