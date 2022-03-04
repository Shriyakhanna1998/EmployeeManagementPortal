from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TelField, DateField
from wtforms.validators import Length, Email, DataRequired


# Form to create employee's credentials
class CreateUser(FlaskForm):
    username = StringField(label='User Name:', validators=[Length(min=3, max=30), DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    confirm_password = PasswordField(label='Confirm Password:', validators=[Length(min=6), DataRequired()])
    submit = SubmitField(label="Register Now")


# Form to fill details of the employee
class RegistrationForm(FlaskForm):
    first_name = StringField(label='First Name:', validators=[Length(min=3, max=30), DataRequired()])
    last_name = StringField(label='Last Name:', validators=[Length(min=3, max=30), DataRequired()])
    email = EmailField(label='Email:', validators=[Email(), Length(min=3, max=30), DataRequired()])
    phone_no = TelField(label='Phone Number:', validators=[Length(10), DataRequired()])
    dob = DateField(label='Date of Birth:', validators=[ DataRequired()])
    address = StringField(label='Address:', validators=[Length(min=3, max=50), DataRequired()])
    submit = SubmitField(label="Submit")


# Form to log in into their respective account according to their roles.
class LoginForm(FlaskForm):
    username = StringField(label='User Name:')
    password = PasswordField(label='Password:')
    submit = SubmitField(label="Login")