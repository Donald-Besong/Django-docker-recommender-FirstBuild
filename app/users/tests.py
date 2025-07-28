# from django.test import TestCase # we can use  django.test´s TestCase
#because there is no actual database yet

from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from users.models import Profile
import unittest

class ProfileModelTest(unittest.TestCase):
    @patch('users.models.Profile.save')
    @patch('users.models.Profile.objects.create')
    def test_profile_creation_and_str(self, mock_create, mock_save):
        # Setup mocks
        mock_user = MagicMock(spec=User)
        mock_user.username = 'mockuser'
        mock_user._state = MagicMock() 

        # Mock Profile.objects.create to return a Profile instance with mock_user
        mock_create.return_value = Profile(user=mock_user)

        # Call the create method (which is mocked)
        profile = Profile.objects.create(user=mock_user)

        # Call save method (mocked)
        profile.save()

        # Assert the __str__ method works with the mocked user
        self.assertEqual(str(profile), 'mockuser Profile')

        # Verify mocked methods were called
        mock_create.assert_called_once()
        mock_save.assert_called_once()

# Recommended to be run using pytest
