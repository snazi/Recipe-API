from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def sample_user(email='test@amadora.com', password='testpass'):
    """
    return a user for testing our models.
    """
    return get_user_model().objects.create_user(email,password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        # test creating a new user with an email is successful
        email = 'test@angelo.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        #test if email becomes normalized
        email = 'test@ANGELO.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        # test if user with no email raises an error
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'askjfdh')

    def test_create_new_superuser(self):
        # Test creating a super user
        user = get_user_model().objects.create_superuser(
            'test@angelo.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """
        Test the tag's string representation
        """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Meat'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """
        Test the ingredient string respresentation
        """

        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Lemon'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """
        Test the recipe string representation
        """

        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Champorado',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)
    # This is basically telling us that i need a uuid format of uuid version 4
    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """
        Test that image is saved in the correct location
        """
        # Any name will do
        uuid = 'test-uuid'
        # In order to use this line of code I have to have done @patch() from above. This forces the mockuid to become the uid specified
        mock_uuid.return_value = uuid
        # The function I plan to make. This function will return the path of the image we uploaded.
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')
        # I expect it to be saved in this path
        exp_path = f'uploads/recipe/{uuid}.jpg'
        # Test if its the path I wanted.
        self.assertEqual(file_path, exp_path)