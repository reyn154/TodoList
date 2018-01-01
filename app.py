from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/todo'

db = SQLAlchemy(app)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(200))
    complete = db.Column(db.Integer)

@app.route('/')
def index():
    tasks = Tasks.query.all()
    return render_template('index.html', tasks = tasks)

@app.route('/add', methods = ['POST'])
def add():
    task = Tasks(text = request.form['todoTask'], complete = 0)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == 'main':
    url = 'http://127.0.0.1:5000'
    app.run(debug = True)
