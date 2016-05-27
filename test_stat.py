import os
import unittest
import tempfile
import msgpack
import server_stat


class StatsTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, server_stat.app.config['DATABASE'] = tempfile.mkstemp()
        server_stat.app.config['TESTING'] = True
        self.app = server_stat.app.test_client()
        server_stat.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(server_stat.app.config['DATABASE'])

    def createPayload(self, logs):
        payload = []
        for row in logs:
            payload.append(row.strip().split(','))
        return msgpack.packb(payload)

    def test_single_sign_up(self):
        logs = ['1464338130000921956,signup,user1']

        self.app.post('/submit', data=self.createPayload(logs))
        rv = self.app.get('/dau')
        assert '["2016-05-27", 1]' in rv.data

    def test_multiple_sign_up(self):
        logs = ['1464247932000921956,signup,user1',
                '1464275715000835443,signup,user2']

        self.app.post('/submit', data=self.createPayload(logs))
        rv = self.app.get('/dau')
        assert '["2016-05-26", 2]' in rv.data

    def test_multiple_activities(self):
        logs = ['1464247932000921956,signup,user1',
                '1464275715000835443,signup,user2',
                '1464338130000921956,follow,user1,user2',
                '1464249967836746281,viorama,user1,splash1',
                '1464249987836746281,viorama,user2,splash2']

        self.app.post('/submit', data=self.createPayload(logs))
        rv = self.app.get('/dau')
        assert '["2016-05-26", 2]' in rv.data
        assert '["2016-05-27", 1]' in rv.data

    def test_multiple_activities_one_by_one(self):
        logs = ['1464247932000921956,signup,user1']
        self.app.post('/submit', data=self.createPayload(logs))
        rv = self.app.get('/dau')
        assert '["2016-05-26", 1]' in rv.data

        logs = ['1464275715000835443,signup,user2']
        self.app.post('/submit', data=self.createPayload(logs))
        rv = self.app.get('/dau')
        assert '["2016-05-26", 2]' in rv.data

        logs = ['1464338130000921956,follow,user1,user2']
        self.app.post('/submit', data=self.createPayload(logs))
        rv = self.app.get('/dau')
        assert '["2016-05-27", 1]' in rv.data

if __name__ == '__main__':
    unittest.main()
