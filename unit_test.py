import unittest
from unittest.mock import patch
from flask import json
from server import app  # Import Flask app from server.py

class TestFlaskFirebase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('server.db.reference')  # Correct mock path to reference where it's used in server.py
    def test_update_levels(self, mock_db_ref):
        # Setup the mock
        mock_ref = mock_db_ref.return_value
        mock_push = mock_ref.push

        # Test data
        data = {'food_level': 'high', 'water_level': 'low'}
        
        # Send a POST request to the Flask app
        response = self.app.post('/api/update_levels', data=json.dumps(data), content_type='application/json')
        
        # Assertions to check the behavior
        self.assertEqual(response.status_code, 200)
        mock_push.assert_called_once_with({
            'food_level': 'high',
            'water_level': 'low'
        })
        self.assertIn('Data updated in Firebase', response.data.decode())

    @patch('server.db.reference')  # Correct mock path to reference where it's used in server.py
    def test_retrieve_food_level(self, mock_db_ref):
        # Setup the mock
        mock_ref = mock_db_ref.return_value
        mock_ref.get.return_value = {'food_level': 'high'}

        # Send a GET request to the Flask app
        response = self.app.get('/api/food_level')

        # Assertions to check the behavior
        self.assertEqual(response.status_code, 200)
        self.assertIn('high', response.data.decode())


if __name__ == '__main__':
    unittest.main()
