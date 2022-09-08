from flask import render_template, redirect, url_for

from . import main
from .forms import ParametersForm


@main.route('/', methods=['GET', 'POST'])
def home():
    parameters_from = ParametersForm()
    if parameters_from.validate_on_submit():
        print(parameters_from.data)
        return redirect(url_for('main.home'))

    return render_template("main/home.html", parameters_from=parameters_from), 200
