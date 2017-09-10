"""
This script will create the index for the node table in the lkb application.
If the index exists, it will be removed and recreated.
"""

# import datetime
import os.path
import shutil
import sqlite3
from lib import my_env
from whoosh.index import create_in
from whoosh.fields import *
# from whoosh.qparser import QueryParser

# Check if directory exists - remove if so...
if os.path.exists("index"):
    shutil.rmtree("index")
os.mkdir("index")

schema = Schema(title=TEXT(stored=True), body=TEXT, created=DATETIME(stored=True), nid=ID(stored=True))
ix = create_in("index", schema)
writer = ix.writer()

db_conn = sqlite3.connect("C:\\Development\\python\\iaas\\lkb\\data\\lkb.db")
db_conn.row_factory = sqlite3.Row
db_cur = db_conn.cursor()
query = "SELECT * FROM node"
db_cur.execute(query)
rows = db_cur.fetchall()
li = my_env.LoopInfo("Index Nodes", 20)
for node in rows:
    writer.add_document(title=node['title'], body=node['body'],
                        created=datetime.datetime.fromtimestamp(node['created']), nid=str(node['nid']))
    li.info_loop()
li.end_loop()
writer.commit()