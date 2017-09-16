import logging
import sqlite3
import time
from . import db, lm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm.exc import NoResultFound


class Node(db.Model):
    """
    Table containing the information of the database.
    Relationship type is called: Adjacency list.
    """
    __tablename__ = "node"
    nid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('node.nid'), nullable=False)
    created = db.Column(db.Integer, nullable=False)
    modified = db.Column(db.Integer, nullable=False)
    revcnt = db.Column(db.Integer)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text)
    children = db.relationship("Node",
                               backref=db.backref('parent', remote_side=[nid])
                               )

    @staticmethod
    def add(**params):
        params['created'] = int(time.time())
        params['modified'] = params['created']
        params['revcnt'] = 1
        node_inst = Node(**params)
        db.session.add(node_inst)
        db.session.commit()
        db.session.refresh(node_inst)
        # Add node to the Search Index
        # ss.node_add(node_inst)
        return node_inst.nid

    @staticmethod
    def edit(**params):
        node_inst = db.session.query(Node).filter_by(nid=params['nid']).first()
        print(node_inst.body)
        node_inst.title = params['title']
        node_inst.body = params['body']
        node_inst.modified = int(time.time())
        node_inst.revcnt += 1
        db.session.commit()
        return

    @staticmethod
    def delete(nid):
        node_inst = Node.query.filter_by(nid=nid).one()
        db.session.delete(node_inst)
        db.session.commit()
        return True


class History(db.Model):
    """
    Table remembering which node is selected when.
    """
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nid = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)

    @staticmethod
    def add(nid):
        params = dict(
            timestamp=int(time.time()),
            nid=nid
        )
        hist_inst = History(**params)
        db.session.add(hist_inst)
        db.session.commit()
        return


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), index=True, unique=True)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register(username, password):
        user = User()
        user.username = username
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def update_password(user, password):
        user.password_hash = generate_password_hash(password)
        db.session.commit(user)
        return

    def __repr__(self):
        return "<User: {user}>".format(user=self.username)


def init_session(dbconn, echo=False):
    """
    This function configures the connection to the database and returns the session object.

    :param dbconn: Name of the sqlite3 database.

    :param echo: True / False, depending if echo is required. Default: False

    :return: session object.
    """
    conn_string = "sqlite:///{db}".format(db=dbconn)
    engine = set_engine(conn_string, echo)
    session = set_session4engine(engine)
    return session


def set_engine(conn_string, echo=False):
    engine = create_engine(conn_string, echo=echo)
    return engine


def set_session4engine(engine):
    session_class = sessionmaker(bind=engine)
    session = session_class()
    return session


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_breadcrumb(nid, bc=None):
    """
    This function will get the breadcrumb for the node. It will find the parent's node until root
    (there is no more node)

    :param nid:

    :param bc: Breadcrumb list so far

    :return: bc
    """
    if not bc:
        bc = []
    node = get_node_attribs(nid=nid)
    if node.parent_id == -1:
        # Found the root node
        return bc
    else:
        parent = get_node_attribs(nid=node.parent_id)
        # bc.append(parent)
        bc[:0] = [parent]
        return get_breadcrumb(parent.nid, bc)


def get_node_attribs(nid):
    """
    This method will collect the attributes required to display a node.

    :param nid: Node ID for the node

    :return: Dictionary with the attributes required to display the node.
    """
    node = Node.query.filter_by(nid=nid).one()
    return node


def get_node_list(order="created"):
    """
    This method will return the most recent posts.

    :param order: This specifies the order for the list. Options: created (default), modified

    :return:
    """
    node_order = Node.created.desc()
    if order == "modified":
        node_order = Node.modified.desc()
    node_list = Node.query.order_by(node_order).limit(15).all()
    return node_list


def search_term(term):
    """
    Trying to work from https://www.sqlite.org/fts5.html
    :param term:
    :return:
    """
    sc = sqlite3.connect(':memory:')
    with sc:
        sc.row_factory = sqlite3.Row
        sc_cur = sc.cursor()
        query = "CREATE VIRTUAL TABLE nodes USING fts5(nid UNINDEXED, title, body, created UNINDEXED)"
        sc.execute(query)
        nodes = Node.query.all()
        for node in nodes:
            query = "INSERT INTO nodes (nid, title, body, created) VALUES (?, ?, ?, ?)"
            sc_cur.execute(query, (node.nid, node.title, node.body, node.created))
        logging.info("Table populated")
        query = "SELECT * FROM nodes WHERE nodes MATCH ? ORDER BY bm25(nodes)"
        res = sc_cur.execute(query, (term, ))
        return res
