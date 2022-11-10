import uuid
from datetime import datetime

from app import app
from flask import render_template, request, redirect, url_for, session, g, flash, jsonify
from wtforms.fields.html5 import DateField
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, QuestionForm
from app.models import User, Questions, Results, Sessions
from app import db
from result_counter import get_user_results, get_methodic


@app.before_request
def before_request():
    g.user = None
    g.question = None

    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        g.user = user

@app.route('/')
def home():
    session['start_time'] = None
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        if user is None:
            user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        session['s_uid'] = str(uuid.uuid4())
        session['user_id'] = user.id
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
        return redirect(url_for('home'))
    if g.user:
        return redirect(url_for('home'))
    return render_template('login.html', form=form, title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.lower(), email=form.email.data.lower(), birthdate=form.birthdate.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session['s_uid'] = str(uuid.uuid4())
        session['user_id'] = user.id
        return redirect(url_for('home'))
    if g.user:
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/question/<int:id>', methods=['GET', 'POST'])
def question(id):
    form = QuestionForm()
    q = Questions.query.filter_by(q_id=id).first()
    if not session.get('s_uid'):
        session['s_uid'] = str(uuid.uuid4())
    if not q:
        return redirect(url_for('score'))
    if not g.user:
        return redirect(url_for('register'))
    if request.method == 'GET':
        session['question_start_time'] = datetime.utcnow()

    # print(g.instr, q.instr)
    # if q.instr != g.instr:
    #     g.instr = q.instr
    #     g.show_instr = g.instr
    # else:
    #     g.instr = None

    if id == 1 and session.get('start_time') is None:
        session['start_time'] = datetime.utcnow()
        answ_session = Sessions(s_uid=session['s_uid'], u_id=g.user.id, start_time=session['start_time'])
        db.session.add(answ_session)
        db.session.commit()
    if request.method == 'POST':
        option = request.form.get('options', default=None)
        if option is None:
            flash("Вам нужно выбрать вариант ответа!")
            return redirect(url_for('question', id=id))
        if option:
            result = Results(u_id=g.user.id, s_uid=session['s_uid'], q_id=id, question=q, answ=option,
                             q_requested_timestamp=session['question_start_time'], timestamp=datetime.utcnow())
            db.session.add(result)
            db.session.commit()
        return redirect(url_for('question', id=(id+1)))
    all_choices = [q.a, q.b, q.c, q.d, q.e, q.f, q.g]
    form.options.choices = [(x, x) for x in all_choices if x]
    return render_template('question.html', form=form, q=q, title='Question {}'.format(id))


@app.route('/score')
def score():
    if not g.user:
        return redirect(url_for('register'))
    session['end_time'] = datetime.utcnow()
    answ_session = Sessions(s_uid=session['s_uid'], u_id=g.user.id, end_time=session['end_time'])
    db.session.add(answ_session)
    db.session.commit()
    return render_template('score.html', title='Final Score')

@app.route('/logout')
def logout():
    if not g.user:
        return redirect(url_for('login'))
    session.pop('user_id', None)
    session.pop('s_uid', None)
    session.pop('marks', None)
    return redirect(url_for('home'))

@app.route('/results', methods=['GET','POST'])
def results():
    if request.method == "POST":
        login = request.form['login']
        if login:
            res = get_user_results(get_methodic(1), login.lower())
            # print(res)
            if res.results_counted:
                # res = {k: str(v) for k, v in res.results_counted}
                return jsonify({'output': str(res.results_counted)})#res.results_counted)
        return jsonify({'output': 'Нет такого логина или пользователь не заполнил методику до конца'})
    return render_template('result.html')
