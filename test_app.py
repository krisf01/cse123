from flask_testing import TestCase
from flask import json
from server import app  # Import your Flask app

class MyTest(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_receive_data(self):
        response = self.client.post('/api/receive_data', data=json.dumps({"food_level": "high", "water_level": "low"}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "Data successfully received")

    def test_food_level(self):
        response = self.client.get('/api/food_level')
        self.assertEqual(response.status_code, 200)
        self.assertIn('food_level', response.json)

    def setUp(self):
        """ Setup a default status file before each test. """
    with open('status.json', 'w') as file:
        json.dump({'food_level': 'high', 'water_level': 'low'}, file)

if __name__ == '__main__':
    from unittest import main
    main()
