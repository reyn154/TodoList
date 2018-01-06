from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy, SessionBase
from flask_login import LoginManager, UserMixin, login_user
from wtforms import Form, StringField, PasswordField, BooleanField, validators
from passlib.hash import sha256_crypt
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

app.secret_key = 'my unobvious secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/todo'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(200))
    complete = db.Column(db.Integer)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))

class RegistrationForm(Form):
    username = StringField('Username')
    email = StringField('Email Address')
    password = PasswordField('Password', {validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Passwords must match")})
    confirm = PasswordField('Confirm Password')
    acceptTos = BooleanField('I accept the Terms of Service',
                             [validators.DataRequired()])

class LoginForm(Form):
    username = StringField('Username', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired()])
    remember = BooleanField('Remember')

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def index():
    tasks = Tasks.query.filter(Tasks.complete == 0)
    completedTasks = Tasks.query.filter(Tasks.complete == 1)
    return render_template('index.html', tasks = tasks, completedTasks = completedTasks)

@app.route('/register', methods =['GET','POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        newUsername = form.username.data
        newEmail = form.email.data
        newPassword = sha256_crypt.encrypt(str(form.password.data))
        query = Users.query.filter(Users.username == newUsername).first()

        if query is not None:
            flash("Username is taken")
            return render_template('register.html', form = form)
        else:
            user = Users(username = newUsername, email = newEmail, password = newPassword)
            db.session.add(user)
            db.session.commit()
            flash("Registration Successful!")
            session['logged_in'] = True
            session['username'] = newUsername
            return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
        user = Users.query.filter(Users.username == form.username.data).first()
        if user:
            if sha256_crypt.verify(str(form.password.data), str(user.password)):
                return "Logged in!"
    return render_template('login.html', form=form)

@app.route('/add', methods = ['POST'])
def add():
    task = Tasks(text = request.form['todoTask'], complete = 0)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update', methods = ['POST'])
def update():
    data = dict(request.form)
    for key in data:
        task = Tasks.query.filter(Tasks.id == key).first()
        task.complete = 1
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/test')
def tester():
    return render_template('templateHome.html')

if __name__ == 'main':
    url = 'http://127.0.0.1:5000'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug = True)
