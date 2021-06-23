import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

current_category = 'History'

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  formatted_questions = [question.format() for question in selection]
  current_questions = formatted_questions[start:end]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  # allow cross-domain access to all the server routes which start with /api
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  setup_db(app)

  # define CORS policy
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  @app.route('/')
  def app_root():
    return "<h1>Trivia app root</h1>"

  # endpoint to handle GET requests for all available categories
  @app.route('/api/v1.0/categories', methods=['GET'])
  def categories():
    categories_query = Category.query.all()

    categories_list = [category.format() for category in categories_query]

    categories_dict = {}
    for cat in categories_list:
        categories_dict[cat['id']] = cat['type']

    return jsonify({
        'success': True,
        'categories': categories_dict
    })

  # endpoint to handle GET requests for paginated questions
  @app.route('/api/v1.0/questions', methods=['GET'])
  def get_questions():
    questions_query = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questions_query)

    if len(current_questions) == 0:
      abort(404)

    categories_query = Category.query.all()
    categories_list = [category.format() for category in categories_query]
    categories_dict = {}
    for cat in categories_list:
        categories_dict[cat['id']] = cat['type']

    # response body
    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions_query),
        'currentCategory': current_category,
        'categories': categories_dict
        })

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404

  # endpoint to handle DELETE requests using a question ID
  @app.route('/api/v1.0/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    error = False
    try:
        question = Question.query.get(question_id)
        db.session.delete(question)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        if error:
          abort(404)
        else:
          return jsonify({"success": True})

  # endpoint to handle POST requests using a question ID
  @app.route('/api/v1.0/questions', methods=['POST'])
  def add_question():
    question_request = request.get_json()
    error = False
    try:
      question_record = Question(**question_request)
      db.session.add(question_record)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
      if error:
        abort(404)
      else:
        return jsonify({"success": True})

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    