import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaAppTestCase(unittest.TestCase):
    """This class represents the Trivia App test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.user_name = "roberto"
        self.database_path = "postgresql://{}@{}/{}".format(self.user_name,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after each test"""
        pass

    def test_categories(self):
        """Test Categories"""
        res = self.client().get('/api/v1.0/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_paginated_questions(self):
        """Performs a simulated GET request to '/questions?page'"""
        res = self.client().get('/api/v1.0/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/api/v1.0/questions?page=1000', content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        self.assertTrue(res.content_type == 'application/json')

    def test_delete_existing_question(self):
        """Performs a simulated DELETE request to '/questions/2'"""
        res = self.client().delete('/api/v1.0/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
    
    def test_delete_nonexisting_question(self):
        """Performs a simulated DELETE request to '/api/v1.0/questions/10000'"""
        res = self.client().delete('/api/v1.0/questions/10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_post_new_question(self):
        """Performs a simulated POST request to '/api/v1.0/questions'"""
        new_question = {'question': 'Heres a new question string',
                        'answer': 'Heres the answer string',
                        'difficulty': 1,
                        'category': 2
                       }
        res = self.client().post('/api/v1.0/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_questions_based_on_existing_category(self):
        """Performs a simulated GET request to '/api/v1.0/categories/1/questions'"""
        res = self.client().get('/api/v1.0/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])
        self.assertTrue(len(data['questions']))

    def test_questions_based_on_nonexisting_category(self):
        """Performs a simulated GET request to '/api/v1.0/categories/1000/questions'"""
        res = self.client().get('/api/v1.0/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()