from flask import render_template
from . import main
from ..models import Role, User, Strategy
from .. import db
from flask_login import login_required

@main.route('/')
def index():
    return render_template('index.html')



@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    strategies = user.strategies.order_by(Strategy.timestamp.desc()).all()
    return render_template('user.html', strategies=strategies)



@main.route('/user/<username>/delete/<strategyname>')
@login_required
def delete(username, strategyname):
	user = User.query.filter_by(username=username).first_or_404()
	strategy = user.strategies.filter_by(strategyname=strategyname).first()
	db.session.delete(strategy)
	db.session.commit()
	strategies = user.strategies.order_by(Strategy.timestamp.desc()).all()
	return render_template('user.html', strategies=strategies)