#!/usr/bin/env python

from flask import Flask, jsonify, request, make_response, abort
from constants import Urls
from user import User
from dbconn import DBConn
from mood import Mood

mood_app = Flask(__name__)


@mood_app.errorhandler(404)
def resource_not_found(error):
    """
    handle 404's (not found)
    """
    return make_response(jsonify({'error': 404, 'error_message': 'resource not found'}), 404)


@mood_app.errorhandler(400)
def bad_request(error):
    """
    handle 400's (bad request)
    """
    return make_response(jsonify({'error': 'We can\'t make sense of that request'}), 400)


@mood_app.errorhandler(401)
def auth_failed(error):
    """
    handle 401's (Unauthorized)
    """
    return make_response(jsonify({'error': 'Unauthorized/login failed'}), 401)


@mood_app.errorhandler(500)
def internal_server_error(error):
    """
    handle 500's (internal server error)
    """
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)


@mood_app.teardown_appcontext
def shutdown_connection(exception):
    """
    close connection on app shutdown
    """
    db.close_connection(exception)


@mood_app.route(Urls.base)
def index():
    return "up and running"


@mood_app.route(Urls.login, methods=['POST'])
def login():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        abort(400)
    key = user.login_user(request.json['username'], request.json['password'])
    if not key:
        abort(401)
    return make_response(jsonify({
        'key': key,
        'message': 'Please place this key in a header called key for further requests'
    }))


@mood_app.route(Urls.mood, methods=['GET', 'POST'])
def access_mood():
    user_id = user.check_auth(request.headers.get('key'))
    if not request.headers.get('key') or not user_id:
        abort(401)
    if request.method == 'POST':
        if not request.json or not 'mood' in request.json:
            abort(400)
        # set mood for this user
        streak = mood.save_mood(user_id, request.json['mood'])
        if streak is not False:
            return make_response(jsonify({
                'message': 'Success, mood saved',
                'streak': streak
            }), 201)
        else:
            abort(500)
    else:
        # return list of moods for this user
        moods = mood.get_moods(user_id)
        if moods is not False:
            # have to unwrap list of tuples format
            return make_response(jsonify({'moods': [mood[0] for mood in moods] or "No moods found"}))
        else:
            abort(500)


@mood_app.route(Urls.streak, methods=['GET'])
def get_streak():
    user_id = user.check_auth(request.headers.get('key'))
    if not request.headers.get('key') or not user_id:
        abort(401)
    # return current streak for this user
    streak = mood.get_streak(user_id)
    if streak is not False:
        return make_response(jsonify({'streak': streak or 0}))
    else:
        abort(500)


@mood_app.route(Urls.percentile, methods=['GET'])
def get_percentile():
    user_id = user.check_auth(request.headers.get('key'))
    if not request.headers.get('key') or not user_id:
        abort(401)
    # return current streak for this user
    percentile = mood.get_max_streak_percentile(user_id)
    if percentile is not False:
        return make_response(jsonify({'percentile': percentile or 0}))
    else:
        abort(500)


if __name__ == '__main__':
    db = DBConn()
    user = User()
    mood = Mood()
    mood_app.run(debug=True, host='0.0.0.0')
