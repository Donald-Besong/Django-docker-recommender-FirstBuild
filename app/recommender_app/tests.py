# from django.test import TestCase # not used because there is no database
# Instead, unittest.TestCase):
# will be used

# test_forms.py

import unittest
from unittest.mock import MagicMock, patch
from recommender_app.forms import MoviesForm
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, TestCase # SimpleTestCase for mocking the db
from django.urls import reverse
from django.test import Client
from recommender_app.models import MoviesRead
from django.contrib.auth.models import User
import datetime
from types import SimpleNamespace

class MoviesFormTest(unittest.TestCase):

    @patch('recommender_app.forms.MoviesRead')  # Mock the model to avoid DB interactions
    def test_valid_form(self, mock_model):
        # Mock the instance returned by the form's Meta.model
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance

        # Create a dummy file to mimic a user upload
        test_file = SimpleUploadedFile("test.csv", b"some,csv,content")

        form_data = {'title': 'My Movie'}
        form_files = {'file_name': test_file}
        form = MoviesForm(data=form_data, files=form_files)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'My Movie')
        self.assertEqual(form.cleaned_data['file_name'].name, 'test.csv')
        # self.assertEqual(form.cleaned_data['file_name'].content_type, 'text/csv') 
        # self.assertTrue(form.cleaned_data['file_name'].name.endswith('.csv'))

    @patch('recommender_app.forms.MoviesRead')
    def test_missing_title(self, mock_model):
        test_file = SimpleUploadedFile("test.csv", b"some,csv,content")
        form_data = {}  # Missing 'title'
        form_files = {'file_name': test_file}
        form = MoviesForm(data=form_data, files=form_files)

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    @patch('recommender_app.forms.MoviesRead')
    def test_default_file(self, mock_model):
        form_data = {'title': 'My Movie'}
        form_files = {}  # Missing file_name
        form = MoviesForm(data=form_data, files=form_files)

        self.assertTrue(form.is_valid())
        self.assertNotIn('file_name', form.errors)

class MoviesReadListViewIntegrationTest(SimpleTestCase):

    @patch('recommender_app.views.render')  # ✅ Prevent DB access during template rendering
    @patch('recommender_app.views.PostListView.get_queryset')  # ✅ Prevent DB access in the view
    def test_movies_read_list_view_with_mocking(self, mock_get_queryset, mock_render):
        client = Client()

        # Create a mock user
        mock_user = MagicMock(spec=User)
        mock_user.username = 'testuser'

        # Create mock MoviesRead instances
        mock_movie_1 = SimpleNamespace(
        title='Movie 1',
        author=mock_user,
        date_posted=datetime.datetime(2025, 7, 14, 12, 0, 0)
        ) 
           
        mock_movie_2 = SimpleNamespace(
        title='Movie 2',
        author=mock_user,
        date_posted=datetime.datetime(2025, 7, 13, 12, 0, 0)
        )
        
        # Provide mock queryset
        mock_queryset = [mock_movie_1, mock_movie_2]
        mock_get_queryset.return_value = mock_queryset

        # Mock the render return value to simulate a response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_render.return_value = mock_response

        # Call the view
        url = reverse('home')
        response = client.get(url)

        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_get_queryset.assert_called_once()
        #mock_render.assert_called_once() # Django class-based views like ListView do not call django.shortcuts.render().
        # Instead, they call an internal method called render_to_response().
        # so use this instead
        mock_render.assert_not_called()
