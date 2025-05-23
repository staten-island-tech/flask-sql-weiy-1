from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wordle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(5), unique=True, nullable=False)

def update_keyboard_status(keyboard, guess, target):
    guess_used = [False] * 5
    target_used = [False] * 5

    for i in range(5):
        if guess[i] == target[i]:
            keyboard[guess[i]] = 'correct'
            guess_used[i] = True
            target_used[i] = True

    for i in range(5):
        if not guess_used[i] and guess[i] in target:
            for j in range(5):
                if not target_used[j] and guess[i] == target[j]:
                    if keyboard.get(guess[i]) != 'correct':
                        keyboard[guess[i]] = 'partial'
                    target_used[j] = True
                    break
            else:
                if keyboard.get(guess[i]) not in ['correct', 'partial']:
                    keyboard[guess[i]] = 'incorrect'
        elif guess[i] not in target and keyboard.get(guess[i]) not in ['correct', 'partial']:
            keyboard[guess[i]] = 'incorrect'



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'target_word' not in session:
        word = Word.query.order_by(db.func.random()).first()
        if not word:
            flash("no word in database, u can add some here")
            return redirect(url_for('admin'))
        session['target_word'] = word.text.upper()
        session['guesses'] = []
        session['keyboard'] = {}

    target = session['target_word']
    guesses = session.get('guesses', [])
    keyboard = session.get('keyboard', {})

    if request.method == 'POST':
        guess = request.form.get('guess', '').upper()
        if len(guess) == 5 and guess.isalpha():
            if guess not in guesses:
                guesses.append(guess)
                update_keyboard_status(keyboard, guess, target)
                session['guesses'] = guesses
                session['keyboard'] = keyboard

                if guess == target:
                    flash(f'🎉 woa u got it the word was {target}')
                    return redirect(url_for('reset'))

                if len(guesses) >= 6:
                    flash(f"❌ o noes u lose. word was {target}")
                    return redirect(url_for('reset'))
            else:
                flash("u geusses that already")
        else:
            flash("u need enter 5 letter word")

        return redirect(url_for('game'))

    return render_template('game.html', guesses=guesses, target=target, keyboard=keyboard)

@app.route('/reset')
def reset():
    session.pop('target_word', None)
    session.pop('guesses', None)
    session.pop('keyboard', None)
    return redirect(url_for('game'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_word = request.form.get('word', '').lower()
        if len(new_word) == 5 and new_word.isalpha():
            if not Word.query.filter_by(text=new_word).first():
                db.session.add(Word(text=new_word))
                db.session.commit()
                flash("✅ word adde")
            else:
                flash("⚠️ word already existings")
        else:
            flash("❌ it need to be 5 letter")
        return redirect(url_for('admin'))

    words = Word.query.all()
    return render_template('admin.html', words=words)

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
