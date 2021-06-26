import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

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
        'current_category': None,
        'categories': categories_dict
        })

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
    try:
      question_request = request.get_json()
      question_record = Question(**question_request)
    except:
      abort(400)
    error = False
    try:
      db.session.add(question_record)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
      if error:
        abort(422)
      else:
        return jsonify({"success": True})

  # endpoint to retrieve questions based on a search term
  @app.route('/api/v1.0/questions/search', methods=['POST'])
  def search_question():
    search_request = request.get_json()
    search_term = search_request["searchTerm"]
    # Case-insensitive search on questions with partial string search
    query_term = "%%"+search_term+"%%"
    query_result = db.session.query(Question).filter(Question.question.ilike(query_term)).all()
    total_questions = len(query_result)
    if total_questions == 0:
      abort(404)

    response = {"questions": [], "total_questions": total_questions, "current_category": None}
    for question in query_result:
      response["questions"].append({'id': question.id,
                                    'question': question.question,
                                    'answer': question.answer,
                                    'difficulty': question.difficulty,
                                    'category': question.category
                                   })
    return jsonify(response)

  # endpoint to handle GET requests to get questions based on category
  @app.route('/api/v1.0/categories/<int:category_id>/questions', methods=['GET'])
  def questions_by_category(category_id):
    try:
      question_query = Question.query.filter(Question.category==category_id)
      total_questions = question_query.count()
      category_query = Category.query.get(category_id)
      category_string = category_query.type
      response = {"questions": [], "total_questions": total_questions, "current_category": category_string}
      for question in question_query:
        response["questions"].append({'id': question.id,
                                      'question': question.question,
                                      'answer': question.answer,
                                      'difficulty': question.difficulty,
                                      'category': question.category
                                      })
      return jsonify(response)
    except:
      abort(404)

  # endpoint to handle POST requests to play the quiz
  @app.route('/api/v1.0/quizzes', methods=['POST'])
  def play_quiz():
    try:
      quizzes_request = request.get_json()
      previous_questions = quizzes_request['previous_questions']
      current_category_id = quizzes_request['quiz_category']['id']
    except:
      abort(400)
    try:
      # get questions based off category
      if(current_category_id == 0):
        questions_in_category = db.session.query(Question.id).all()
      else:
        questions_in_category = db.session.query(Question.id).filter(Question.category == current_category_id).all()

      flat_questions_in_category = [j for sub in questions_in_category for j in sub]
      # filter out previous questions
      filtered_questions_in_category = [question for question in flat_questions_in_category if question not in previous_questions]
      # verify if there are questions left
      if(len(filtered_questions_in_category) == 0):
        response = {"question": None}
      else:
        # get a new random question
        new_question_id = random.choice(filtered_questions_in_category)
        question = Question.query.get(new_question_id)
        response = {"question": question.format()}
      return jsonify(response)
    except:
      abort(404)

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "Bad Request"
      }), 400
      
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
          }), 422
  
  return app

    