"""
This is the whoosh quick intro
"""

import os.path
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
if not os.path.exists("index"):
    os.mkdir("index")
ix = create_in("index", schema)

writer = ix.writer()
writer.add_document(title=u"First document", path=u"/a",
                    content=u"This is the first document we've added!")
writer.add_document(title=u"Second document", path=u"/b",
                    content=u"This is the second document, even more interesting.")
writer.commit()

with ix.searcher() as searcher:
    query = QueryParser("content", ix.schema).parse("first")
    result = searcher.search(query)
    print(result[0])
