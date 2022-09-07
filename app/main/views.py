from flask import jsonify

from . import main


@main.route('/', methods=['GET'])
def home():
    some_data = {"data": "OK"}
    return jsonify(some_data), 200
