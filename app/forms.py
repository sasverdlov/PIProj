from datetime import date

from dateutil.relativedelta import relativedelta
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired("Введите email")])
    password = PasswordField('Password', validators=[DataRequired("Введите пароль")])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired("Введите ФИО")])
    email = StringField('Email', validators=(DataRequired("Введите email"), Email("Введите корректный email")))
    birthdate = DateField('Birthdate', validators=[DataRequired("Введите дату рождения")])
    password = PasswordField('Password', validators=[DataRequired("Введите пароль")])
    password2 = PasswordField('Confirm Password',
                              validators=(DataRequired(), EqualTo('password')))
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Такой пользователь уже зарегистрирован')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Такой email уже зарегистрирован')

    def validate_birthdate(self, birthdate):
        if birthdate.data > date.today() - relativedelta(years=18):
            raise ValidationError('Респонденту должно быть от 18 лет')
        if birthdate.data < date.today() - relativedelta(years=100):
            raise ValidationError('Пожалуйста, введите корректную дату')


class QuestionForm(FlaskForm):
    options = RadioField('Options: ', validators=[DataRequired()], default=1)
    submit = SubmitField('Далее')  # validation on empty submit
