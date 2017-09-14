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
    return nodelist("created")


@main.route('/node/<nid>')
@login_required
def node(nid):
    node_obj = ds.get_node_attribs(nid=nid)
    bc = ds.get_breadcrumb(nid=nid)
    """
    params = dict(
        nid=node_obj.nid,
        title=node_obj.title,
        body=my_env.reformat_body(node_obj.body),
        breadcrumb=bc,
        children=sorted(node_obj.children, key=lambda child: child.title),
        created=node_obj.created
    )
    """
    params = dict(
        node=node_obj,
        breadcrumb=bc
    )
    return render_template('node.html', **params)


@main.route('/node_add/<pid>', methods=['GET', 'POST'])
@login_required
def node_add(pid, nid=None):
    form = NodeAdd()
    title = ""
    if request.method == 'POST':
        if form.validate_on_submit():
            node_vals = dict(
                title=form.title.data,
                body=form.body.data,
                parent_id=form.parent_id.data
            )
            if nid:
                node_vals['nid'] = nid
                ds.Node.edit(**node_vals)
                flash('Node modified', 'info')
            else:
                ds.Node.add(**node_vals)
                flash('Node added', 'info')
    else:
        if nid:
            title = "Edit Node"
            node_vals = ds.Node.query.filter_by(nid=nid).first()
            form.title.data = node_vals.title
            form.body.data = node_vals.body
            form.parent_id.data = node_vals.parent_id
        else:
            title = "Create Node"
            form.parent_id.data = pid
    return render_template('node_add.html', form=form, title=title)


@main.route('/node_edit/<pid>/<nid>', methods=['GET', 'POST'])
@login_required
def node_edit(pid, nid):
    return node_add(pid, nid)


@main.route('/node_delete/<nid>', methods=['GET'])
@login_required
def node_delete(nid):
    flash('Node {nid} deleted'.format(nid=nid), 'warning')
    ds.Node.delete(nid)
    return index()


@main.route('/nodelist/<order>', methods=['GET'])
@login_required
def nodelist(order="created"):
    """
    Returns the nodes in an ordered list.

    :param order: Specifies the order: created (default, most recent first), modified (most recent modified first)

    :return:
    """
    title = "Recent Nodes"
    if order == "modified":
        title = "Last Modified"
    node_list = ds.get_node_list(order)
    params = dict(
        node_list=node_list,
        title=title
    )
    return render_template('node_list.html', **params)


@main.errorhandler(404)
def not_found(e):
    return render_template("404.html", err=e)
