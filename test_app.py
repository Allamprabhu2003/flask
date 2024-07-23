# # test_app.py
# import unittest
# from final import create_app, db
# from final.models import User

# class BasicTests(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.app = create_app('final.config.TestConfig')
#         cls.client = cls.app.test_client()
#         cls.app_context = cls.app.app_context()
#         cls.app_context.push()
#         db.create_all()

#     @classmethod
#     def tearDownClass(cls):
#         db.drop_all()
#         cls.app_context.pop()

#     def test_homepage(self):
#         response = self.client.get('/')
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(b'Welcome', response.data)

#     def test_login(self):
#         response = self.client.post('/login', data={
#             'username': 'testuser',
#             'password': 'testpassword'
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(b'Login Successful', response.data)

#     def test_protected_route(self):
#         self.client.post('/login', data={
#             'username': 'testuser',
#             'password': 'testpassword'
#         })
#         response = self.client.get('/protected', follow_redirects=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(b'Protected Content', response.data)

# if __name__ == '__main__':
#     unittest.main()
