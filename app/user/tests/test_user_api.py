from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test the uysers API in public
    """
    
    def setUp(self):
        """
        instantiate stuff
        """
        self.client = APIClient()
        
    def test_create_valid_user_success(self):
        """
        Test creating user with valid payload is successful
        """
        payload = {
            'email': 'test@amadora.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        # res means response, we're actually using .post() to make a self post request. Given the payload we stated above
        res = self.client.post(CREATE_USER_URL, payload)
        # Now that we've made a response, lets check if its successful. We check if the respononse has a status equal to a status code that defines success.
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # If success, lets check our data using the code below. This grabs the user from our db given the response
        user = get_user_model().objects.get(**res.data)
        # Now we check if the user we got back, is equal to the password we sent.
        print(user)
        self.assertTrue(user.check_password(payload['password']))
        # This is just to make sure that there is no password in our response because thats a security breach.
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """
        Test to see if it fails when we create a user that already exists
        """
        payload = {
            'email': 'test@amadora.com',
            'password': 'testpass',
            'name': 'Test name ahaa'
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_password_too_short(self):
        """
        test if the password is more than 5 characters
        """
        payload = {
            'email': 'test@amadora.com',
            'password': 'pw',
            'name': 'Test',
        }
        # same way we create a user
        res = self.client.post(CREATE_USER_URL, payload)
        # We WANT  a bad request so we're looking for that
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Now we want to check if even though it threw a bad requets, that the user was never made.
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        # the exists() will return true if the modal contains the user email we used in the payload. If the user didnt get created, then its false. We check for the false.
        self.assertFalse(user_exists)


    def test_create_token_for_user(self):
        """
        Test that a token is created for the user
        """
        # same as before, our payload is the username and pass
        payload = {
            'email': 'test@amadora.com', 
            'password': 'testpass'
            }
        # we create a user with the credentials
        create_user(**payload)
        # we make a post request with the URL and the data/payload
        res = self.client.post(TOKEN_URL, payload)
        # assertIn checks if theres a variable called token inside the response.data
        self.assertIn('token', res.data)
        # checks if the request was actually fulfilled.
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_create_token_invalid_credentials(self):
        """
        Test that token is not created if invalid credentials are given
        """
        # Im forcibly making an account since we've already tested it works
        create_user(email='test@amadora.com', password="testpass")
        # heres the account im testing
        payload = {
            'email': 'test@amadora.com', 
            'password': 'wrong'
        }
        # Make a query
        res = self.client.post(TOKEN_URL, payload)
        # Im checking that there isnt a token
        self.assertNotIn('token', res.data)
        # Im check that it failed.
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_create_token_no_user(self):
        """
        Test that token is not created if user doesn't exist
        """
        payload = {
            'email': 'test@amadora.com', 
            'password': 'testpass'
        }
        # remember that all these tests are isolated from one another. I didnt run create user so the payload shouldnt exist
        res = self.client.post(TOKEN_URL, payload)
        # Since it doesnt exist. Django by default should reject it. Our response should not have a token
        self.assertNotIn('token', res.data)
        # This should fail.
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)