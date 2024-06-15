from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models import GameState
from models import db, User
import os
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.before_request
def create_tables():
    if not os.path.exists('users.db'):
        db.create_all()


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('game'))
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/game')
def game():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('game.html')


@app.route('/save_game', methods=['POST'])
def save_game():
    if 'user_id' not in session:
        return jsonify(error='User not logged in'), 403
    data = request.json
    user_id = session['user_id']
    board = json.loads(data['board'])
    print(board)
    game_state = GameState(user_id=user_id, board=json.dumps(board))
    db.session.add(game_state)
    db.session.commit()
    return jsonify(success=True)


@app.route('/load_game', methods=['GET'])
def load_game():
    if 'user_id' not in session:
        return jsonify(error='User not logged in'), 403
    user_id = session['user_id']
    game_state = GameState.query.filter_by(user_id=user_id).order_by(GameState.id.desc()).first()
    if game_state:
        board = json.loads(game_state.board)
        return jsonify(board=board)
    else:
        return jsonify(error='No saved game found'), 404


@app.route('/initialize_game', methods=['POST'])
def initialize_game():
    board = [[0] * 4 for _ in range(4)]
    add_random_tile(board)
    add_random_tile(board)
    session['board'] = board
    return jsonify(board=board)


@app.route('/move', methods=['POST'])
def move():
    if 'board' not in session:
        return jsonify(error='Game not initialized'), 400
    direction = request.json['direction']
    board = session['board']
    if direction == 'left':
        board, moved = move_left(board)
    elif direction == 'right':
        board, moved = move_right(board)
    elif direction == 'up':
        board, moved = move_up(board)
    elif direction == 'down':
        board, moved = move_down(board)
    if moved:
        add_random_tile(board)
    session['board'] = board
    return jsonify(board=board)


def add_random_tile(board):
    empty_tiles = [(i, j) for i in range(4) for j in range(4) if board[i][j] == 0]
    if empty_tiles:
        i, j = random.choice(empty_tiles)
        board[i][j] = 2 if random.random() < 0.9 else 4


def move_left(board):
    moved = False
    new_board = []
    for row in board:
        new_row = [num for num in row if num != 0]
        for i in range(len(new_row) - 1):
            if new_row[i] == new_row[i + 1]:
                new_row[i] *= 2
                new_row[i + 1] = 0
                moved = True
        new_row = [num for num in new_row if num != 0]
        new_board.append(new_row + [0] * (4 - len(new_row)))
    if new_board != board:
        moved = True
    return new_board, moved


def move_right(board):
    moved = False
    new_board = []
    for row in board:
        new_row = [num for num in row if num != 0]
        for i in range(len(new_row) - 1, 0, -1):
            if new_row[i] == new_row[i - 1]:
                new_row[i] *= 2
                new_row[i - 1] = 0
                moved = True
        new_row = [num for num in new_row if num != 0]
        new_board.append([0] * (4 - len(new_row)) + new_row)
    if new_board != board:
        moved = True
    return new_board, moved


def move_up(board):
    moved = False
    new_board = [list(row) for row in zip(*board)]
    new_board, moved = move_left(new_board)
    new_board = [list(row) for row in zip(*new_board)]
    return new_board, moved


def move_down(board):
    moved = False
    new_board = [list(row) for row in zip(*board)]
    new_board, moved = move_right(new_board)
    new_board = [list(row) for row in zip(*new_board)]
    return new_board, moved


if __name__ == '__main__':
    app.run(debug=True)
