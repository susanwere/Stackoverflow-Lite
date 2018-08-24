from flask import Flask, request, flash, redirect, url_for, jsonify, session, abort, render_template, g
from . import api
from .models import Question
from app.users.models import User
from app.jwtfile import Jwt_details
questionObject = Question() 
jwt_obj = Jwt_details()

@api.before_app_request
def before_request():
    """get the user bafore every request"""
    if request.endpoint and 'auth' not in request.url:

        try:
            if request.method != 'OPTIONS':
                auth_header = request.headers.get('authorization')
                g.user = None
                access_token = auth_header.split(" ")[1]
                res = jwt_obj.decode_auth_token(access_token)
                if isinstance(res, int) and not jwt_obj.is_blacklisted(access_token):
                    # check if no error in string format was returned
                    # find the user with the id on the token
                    user = User()
                    response = user.user_by_id(res)
                    g.userid = response['id']
                    g.username = response['username']
                    return
                return jsonify({"message": "Please register or login to continue"}), 401
        except Exception:
            return jsonify({"message": "Authorization header or acess token is missing."}), 400

def validate_data(data):
    """validate request details"""
    try:
        # check if title more than 10 characters
        if len(data['title'].strip()) == 0:
            return "Title cannot be empty"
        elif len(data['body'].strip()) == 0:
            return "Question body cannot be empty"
        elif len(data['title'].strip()) < 5:
            return "Title Must Be more than 5 characters"
        elif len(data['body'].strip()) < 10:
            return "Body must be more than 10 letters"
        else:
            return "valid"
    except Exception as error:
        return "please provide all the fields, missing " + str(error)

@api.route('/questions', methods=["GET", "POST"])
def question():
    """ Method to create and retrieve questions."""
    if request.method == "POST":
        data = request.get_json()
        res = validate_data(data)
        if res == "valid":
            title = data['title']
            body = data['body']
            question = Question(title, body)
            response = question.create()
            return response
        return jsonify({"message":res}), 422
    data = questionObject.get_all_questions()
    return data


@api.route('/questions/<int:id>', methods=["GET", "PUT"])
def question_id(id):
    """ Method to retrieve and update a specific question."""
    if request.method == 'PUT':
        data = request.get_json()
        check_details = validate_data(data)
        if check_details is not "valid":
            return jsonify({"message": check_details}), 400
        else:
            if questionObject.fetch_question_by_id(id) is False:
                return jsonify({"message": "The Question with that ID doesnt exist"}), 404
            else:
                if questionObject.is_owner(id, g.userid) is False:
                    return jsonify({"message": "Sorry you cant edit this request"}), 401
                else:
                    try:
                        title = data['title']
                        body = data['body']
                        req = Question(title, body)
                        res = req.update(id)
                        return jsonify({"message": "Update succesfful", "response": res}), 201
                    except Exception as error:
                        # an error occured when trying to update request
                        response = {'message': str(error)}
                        return jsonify(response), 401

    item = questionObject.fetch_question_by_id(id)
    if item is False:
        return jsonify({"message": "The request doesnt exist"}), 404
    else:
        return jsonify(item), 200

@api.route('/questions/<int:id>', methods=["DELETE"])
def admin_delete(id):
    """ endpoint to delete questions"""
    question_exist = questionObject.fetch_question_by_id(id)
    if not question_exist:
        return jsonify(response="Question does not exist"), 404
    else:
        if questionObject.is_owner(id, g.userid) is False:
            return jsonify({"message": "Sorry you have no permission to delete this question"}), 401
        else:
            try:
                resp = questionObject.delete(id)
                return jsonify(response=resp), 200
            except Exception as error:
                # an error occured when trying to update request
                response = {'message': str(error)}
                return jsonify(response), 401


@api.route('/questions/<int:qid>/answer', methods=["POST"])
def answer(qid):

    """ Method to create and retrieve questions."""
    if 'username' in session:
        data = request.get_json()
        comment = data['comment']
        res = questionObject.add_answer(qid, comment)
        return res
    return jsonify({"message": "Please login to answer a question."})