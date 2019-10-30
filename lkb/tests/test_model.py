"""
This procedure will test the classes of the models_graph.
"""

import unittest
from lkb import create_app
from lkb.lib import db_model as ds
from lib import my_env


# @unittest.skip("Focus on Coverage")
class TestModelGraph(unittest.TestCase):

    def setUp(self):
        # Initialize Environment
        # my_env.init_loghandler(__name__, "c:\\temp\\log", "warning")
        self.app = create_app('testing')
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()

    def tearDown(self):
        self.app_ctx.pop()

    def test_get_node_attribs(self):
        # Get a valid node
        nid = 1072
        node = ds.get_node_attribs(nid)
        self.assertTrue(isinstance(node, ds.Node))
        self.assertTrue('accomplish' in node.body)
        # Find 2 children
        self.assertEqual(len(node.children), 2)
        # Second child is about 'timeline context'
        self.assertTrue('timeline context' in node.children[1].title)
        # Parent node is about 'Website: tuin'
        parent_node = ds.get_node_attribs(nid=node.parent_id)
        self.assertTrue('Website: tuin' in parent_node.title)
        self.assertTrue(isinstance(node.parent.title, str))
        self.assertEqual(node.parent.title, 'Website: tuin')

    def test_node_breadcrumb(self):
        nid = 1074
        bc = ds.get_breadcrumb(nid)
        self.assertTrue(isinstance(bc, list))

    def test_datestamp(self):
        # Test Jinja filter for datestamp
        self.assertEqual(my_env.datestamp(1499999999), "14/07/17 04:39")

    def test_node_modify(self):
        # Test Node Add to parent 854 (CA Unicenter)
        params = dict(
            title="Test Node",
            body="Text with test Node. Abracadabra for search purpuse.",
            parent_id=854
        )
        nid = ds.Node.add(**params)
        # print("Node: {nid}".format(nid=nid))
        node = ds.get_node_attribs(nid)
        self.assertTrue(isinstance(node, ds.Node))
        self.assertTrue('Abracadabra' in node.body)
        # Now try to modify the node
        params["body"] = "Now remove special string and add kweepeer instead."
        params["nid"] = nid
        ds.Node.edit(**params)
        ds.Node.delete(nid)
        # res = ds.search_term("sql")
        # print("Key: {k}".format(k=res.description))

    def test_get_tree(self):
        res = ds.get_tree()
        self.assertTrue(isinstance(res, list))
        lr = len(res)
        self.assertGreater(lr, 1750)
        # Now exclude Verkiezingen
        res = ds.get_tree(exclnid=732)
        self.assertTrue(isinstance(res, list))
        self.assertGreater(lr, len(res))

if __name__ == "__main__":
    unittest.main()
