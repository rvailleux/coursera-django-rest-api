from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase, force_authenticate
from rest_framework.authtoken.models import Token



class test_User(APITestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.domain = "localhost:8000"

        self.validUserPassword = "pass1234"
        self.validUser = User.objects.create_user(
            email="User@test.com", username='user1', password=self.validUserPassword)
        self.validUser.save()

        self.validUserToken = Token.objects.create(user=self.validUser)
        self.validUserToken.save()

    def test_users_post(self):
        '''
        Test user creation through POST /api/users/
        '''
        test_email = 'test@test.com'

        url = f"https://{self.domain}/api/users/"

        self.assertFalse(User.objects.filter(email=test_email).exists())
        response = self.client.post(
            path=url,
            data={'email': test_email, 'username': 'test', 'password': 'passwordtest'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=test_email).exists())

        # cleaning DB
        User.objects.get(email=test_email).delete()

    def test_users_token_post(self):
        '''
        Test getting user token through POST /token/login
        '''
        url = f"https://{self.domain}/token/login/"

        # Test failure when no credential passed
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test failure when bad credential passed
        data = {
            "username": self.validUser.username,
            "password": "1234",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "username": self.validUser.username,
            "password": self.validUserPassword,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()['auth_token'], self.validUserToken.key)

"""     def test_users_me_get(self):
        url = f"https://{self.domain}/api/users/me/"

        # Test unauthenticated call fails
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic'+  base64.b64encode(bytes('{self.validUser.username}:{self.validUserPassword}', 'utf8')).decode('utf8'),
        }
        response = self.client.get(
            url, **auth_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK) """


