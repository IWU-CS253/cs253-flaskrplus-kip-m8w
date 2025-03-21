import os
# import flaskr
import app as flaskr # importing from app.py with our application, with the name flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data

    # test for filtering post
    def test_filter(self):
        rv = self.app.post('/filter', data=dict(
            category='A category'
        ), follow_redirects=True)
        assert b'A category' in rv.data

    # test for deleting post (not written yet)
    # def test_delete(self):
    #     rv = self.app.post('/delete', data=dict(
    #
    #     ), follow_redirects=True)
    #     assert b'123' not in rv.data

    # test for editing post (not written yet)
    # def test_edit(self):
    #     rv = self.app.post('/edit-redir')

if __name__ == '__main__':
    unittest.main()