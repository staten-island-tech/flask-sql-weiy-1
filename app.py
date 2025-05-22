from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wordle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Word model
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(5), unique=True, nullable=False)

# Index page
@app.route('/')
def index():
    return render_template('index.html')

# Game page
@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'target_word' not in session:
        word = Word.query.order_by(db.func.random()).first()
        session['target_word'] = word.text.upper()
        session['guesses'] = []

    if request.method == 'POST':
        guess = request.form.get('guess', '').upper()
        if len(guess) == 5:
            session['guesses'].append(guess)
            if guess == session['target_word']:
                flash('You guessed it!')
        return redirect(url_for('game'))

    return render_template('game.html', guesses=session.get('guesses', []), target=session.get('target_word'))

# Reset game
@app.route('/reset')
def reset():
    session.pop('target_word', None)
    session.pop('guesses', None)
    return redirect(url_for('game'))

# Admin login (simple, no auth)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_word = request.form.get('word', '').lower()
        if len(new_word) == 5 and new_word.isalpha():
            if not Word.query.filter_by(text=new_word).first():
                db.session.add(Word(text=new_word))
                db.session.commit()
                flash("Word added.")
            else:
                flash("Word already exists.")
        else:
            flash("Word must be 5 letters.")
        return redirect(url_for('admin'))

    words = Word.query.all()
    return render_template('admin.html', words=words)

# Delete word
@app.route('/delete/<int:word_id>')
def delete_word(word_id):
    word = Word.query.get(word_id)
    if word:
        db.session.delete(word)
        db.session.commit()
    return redirect(url_for('admin'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
