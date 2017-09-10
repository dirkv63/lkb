# import logging
import lkb.db_model as ds
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from .forms import *
from . import main
from lkb.db_model import User
from lib import my_env


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Login not successful', "error")
            return redirect(url_for('main.login', **request.args))
        login_user(user, remember=form.remember_me.data)
        return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('login.html', form=form, hdr='Login')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/pwdupdate', methods=['GET', 'POST'])
@login_required
def pwd_update():
    form = PwdUpdate()
    if form.validate_on_submit():
        user = ds.load_user(current_user.get_id())
        if user is None or not user.verify_password(form.current_pwd.data):
            flash('Password update not successful', 'error')
            return redirect(url_for('main.pwd_update'))
        # User and password is OK, so update the password
        user.set_password(form.new_pwd.data)
        flash('Password changed!', 'info')
        return redirect(url_for('main.index'))
    return render_template('login.html', form=form, hdr='Change Password')


@main.route('/')
@login_required
def index():
    # This will return the most recent posts
    node_list = ds.get_recent_posts()
    params = dict(
        node_list=node_list
    )
    return render_template('recent_posts.html', **params)


@main.route('/node/<nid>')
@login_required
def node(nid):
    node_obj = ds.get_node_attribs(nid=nid)
    bc = ds.get_breadcrumb(nid=nid)
    params = dict(
        title=node_obj.title,
        body=my_env.reformat_body(node_obj.body),
        breadcrumb=bc,
        children=sorted(node_obj.children, key=lambda child: child.title),
        created=node_obj.created
    )
    return render_template('node.html', **params)


@main.errorhandler(404)
def not_found(e):
    return render_template("404.html", err=e)
