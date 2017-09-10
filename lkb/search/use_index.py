"""
This script will use an existing index.
"""

from whoosh.index import open_dir
from whoosh.qparser import QueryParser

ix = open_dir("index")

with ix.searcher() as searcher:
    query = QueryParser("body", ix.schema).parse("jinja")
    result = searcher.search(query, limit=None)
    for res in result:
        print(res)
