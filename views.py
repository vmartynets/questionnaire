from course import app, db, login_serializer, lm
from flask_login import login_required, login_user, logout_user, current_user
from flask import render_template, redirect, url_for, flash, g
from forms import IndexForm, AddUserForm
from models import User, Teacher, Student, Test, UserProfile, Question
from hashlib import md5
from json import dumps


@lm.user_loader
def load_user(user_id):
    """Flask-Login user_loader callback.
    The user_loader function asks this function to get a User Object or return
    None based on the user_id.
    The user_id was stored in the session environment by Flask-Login.
    user_loader stores the returned User object in current_user during every
    flask request.
    """
    member = Teacher.query.filter_by(user_id=user_id).first()
    if member is None:
        member = Student.query.filter_by(user_id=user_id).first()
        if member is None:
            g.id = 0
        else:
            g.id = member.id
    return User.query.get(int(user_id))


@lm.token_loader
def load_token(token):
    print "LOAD TOKEN"

    """
    Flask-Login token_loader callback.
    The token_loader function asks this function to take the token that was
    stored on the users computer process it to check if its valid and then
    return a User Object if its valid or None if its not valid.
    """

    #The Token itself was generated by User.get_auth_token.  So it is up to
    #us to known the format of the token data itself.

    #The Token was encrypted using itsdangerous.URLSafeTimedSerializer which
    #allows us to have a max_age on the token itself.  When the cookie is stored
    #on the users computer it also has a exipry date, but could be changed by
    #the user, so this feature allows us to enforce the exipry date of the token
    #server side and not rely on the users cookie to exipre.

    max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()

    #Decrypt the Security Token, data = [username, hashpass]
    data = login_serializer.loads(token, max_age=max_age)
    print data

    #Find the User
    user = User.get(data[0])

    #Check Password and return user or None
    if user and data[1] == user.password:
        return user
    return None

def decode(password):
    m = md5(password)
    return m.hexdigest()

@app.route('/', methods=['GET','POST'])
def index():
    form = IndexForm()
    if form.validate_on_submit():#TODO: test for password
        password = decode(form.password.data)
        user =  User.query.filter_by(password = password).first()
        if not user:
            flash('error!')
            print "not exist"
            return redirect(url_for('index'))
        else:
            print "exist"
            login_user(user)
        return redirect(url_for('test', password=form.data))

    return render_template('index.html', form = form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/test', methods=['GET','POST'])
@app.route('/test/', methods=['GET','POST'])
@login_required
def test():
    user_id = current_user.id
    teacher_id = Teacher.query.filter_by(user_id = user_id).first()
    tests = Test.query.filter_by(teacher_id = teacher_id).all()
    print tests

    return render_template('test.html', tests = tests)

@app.route('/add_test', methods=['GET','POST'])
@app.route('/add_test/',methods=['GET','POST'])
@app.route('/add_test/<int:id>', methods=['GET','POST'])
@login_required
def edit_test(id=''):
    if current_user.is_student():
        return redirect(url_for('index'))
    form = 1
    questions = Question.query.filter_by(test_id = id).all
    return render_template('edit_test.html', form=form)


@app.route('/add_user',methods=['GET','POST'])
@app.route('/add_user/',methods=['GET','POST'])
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        password = decode(form.password.data)
        if not User.query.filter_by(password = password).first(): #user doesnt exist
            if form.category.data == 'Teacher':
                sess = db.session()
                user = User(form.email.data, password)
                sess.add(user)
                sess.commit()
                teacher = Teacher(user.id)
                userprofile = UserProfile(user.id,form.realname.data)
                sess.add(userprofile)
                sess.add(teacher)
                sess.commit()
                return redirect(url_for('index'))
        else:
            return "net" #TODO: fix
        print form.password.data
    return render_template('add_user.html',form = form)