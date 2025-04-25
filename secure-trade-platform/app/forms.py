from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, TextAreaField,  SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # 사용자 이름의 고유성 체크
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    # 이메일의 고유성 체크
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Create Product')
    
    # 금액 유효성 체크 (가격은 0원보다 작을 수 없음)
    def validate_price(self, price):
        if price.data <= 0:
            raise ValidationError('Price must be greater than zero.')

class UpdateEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Email')

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')

class ChargeWalletForm(FlaskForm):
    amount = IntegerField('Amount to charge', validators=[DataRequired()])
    submit = SubmitField('Charge Wallet')

class UpdateProfileForm(FlaskForm):
    bio = StringField('Bio', validators=[Length(max=500)])
    submit = SubmitField('Update Profile')

class DeleteAccountForm(FlaskForm):
    submit = SubmitField('Delete Account')

class SearchForm(FlaskForm):
    keyword = StringField('Keyword', validators=[DataRequired()])
    sort_by = SelectField('Sort by', choices=[
        ('latest', 'Latest'),
        ('price_asc', 'Price (Low to High)'),
        ('price_desc', 'Price (High to Low)')
    ])
    submit = SubmitField('Search')

class ReportForm(FlaskForm):
    reason = TextAreaField('신고 사유', validators=[DataRequired(), Length(min=5, max=300)])
    submit = SubmitField('신고하기')

class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Update Password')
