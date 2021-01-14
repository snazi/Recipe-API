import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def image_upload_url(recipe_id):
    """
    Return URL for recipe image upload
    """

    return reverse('recipe:recipe-upload-image', args=[recipe_id])

def detail_url(recipe_id):
    """
    Return recipe detail URL
    """

    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='Main course'):
    """
    Create and return a sample tag
    """

    return Tag.objects.create(user=user, name=name) 

def sample_ingredient(user, name='Cinnamon'):
    """
    Create and return a sample ingredient
    """

    return Ingredient.objects.create(user=user, name=name)

def sample_recipe(user, **params):
    """
    Create and return a sample recipe
    """
    
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 3,
        'price': 99.00
    }

    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)

class PublicRecipeApiTests(TestCase):
    """
    Test unauthenticated recipe API access
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required
        """

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    """
    Test authenticated recipe API access
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@amadora.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """
        Test retrieving a list of recipes
        """
        # Declaring it twice to create 2 recipes
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        # Standard call
        res = self.client.get(RECIPES_URL)
        # Grab all recipes and order them by ID
        recipes = Recipe.objects.all().order_by('-id')
        # Im expecting a list so thats why many=True
        serializer = RecipeSerializer(recipes, many=True)
        # Make sure that the request is valid and not turned down by the server
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check for the data
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """
        Test retrieving recipes for the specific user
        """
        # Apart from the sample user, create another one
        user2 = get_user_model().objects.create_user(
            'other@amadora.com',
            'password123'
        )
        # Make a recipe for the 2nd user
        sample_recipe(user=user2)
        # Make recipe for the 1st
        sample_recipe(user=self.user)
        # Make the call
        res = self.client.get(RECIPES_URL)
        # Grab the list of recipes from the 1st user
        recipes = Recipe.objects.filter(user=self.user)
        # Its a list like before
        serializer = RecipeSerializer(recipes, many=True)
        # Make sure that the request is good
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Im supposed to recieve only 1 recipe since i made only one
        self.assertEqual(len(res.data), 1)
        # Check if the 1 thing retrieved is the data I wanted.
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """
        Test viewing a recipe detail
        """

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """
        Test creating recipe
        """

        payload = {
            'title': 'Chocolate amazing cake',
            'time_minutes': 30,
            'price': 5.00
        }
        
        res = self.client.post(RECIPES_URL, payload)
        # This is new. that HTTP request should return everytime we create something new in the database
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        # This will loop at check the value of the key in the payload because its a dictionary. Getattr allows you to get a key from the object in the 1st parameter.
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """
        Test creating a recipe with tags
        """

        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """
        Test creating recipe with ingredients
        """

        ingredient1 = sample_ingredient(user=self.user, name='Prawns')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')
        payload = {
            'title': 'Thai prawn red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 7.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """
        Test updating a recipe with patch
        """

        # Adding the recipe
        recipe = sample_recipe(user=self.user)
        # Adding our sample tag to our sample recipe
        recipe.tags.add(sample_tag(user=self.user))
        # Creating a new tag to update the recipe with
        new_tag = sample_tag(user=self.user, name='Curry')
        # The payload will contain the name of the title and the Tag to be added.
        payload = {
            'title': 'Chicken tikka', 
            'tags': [new_tag.id]
        }
        # To get into the specific Recipe, I need the ID of the Recipe. I get that here
        url = detail_url(recipe.id)
        # I make the Patch request with the URL and the Payload
        self.client.patch(url, payload)
        # Refresh the db
        recipe.refresh_from_db()
        # Check the recipe. Check if title of the payload and the recipe that I updated are the same
        self.assertEqual(recipe.title, payload['title'])
        # grab all the tags from the recipe
        tags = recipe.tags.all()
        # Im updating the tag inside the recipe with the Tag i made so the recipe's tag should still be 1
        self.assertEqual(len(tags), 1)
        # Check that the new tag is inside the tags
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """
        Test updating a recipe with put
        """

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spaghetti carbonara',
            'time_minutes': 25,
            'price': 5.00
        }
        
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)

class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@amadora.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an email to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)