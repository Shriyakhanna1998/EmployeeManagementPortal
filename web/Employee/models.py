from Employee import db, login_manager
from Employee import bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User table containing credentials of the employee
class User(db.Model, UserMixin):
    __tablename__ = "user"
    user_id = db.Column(db.Integer(), primary_key= True)
    username = db.Column(db.String(length=50), nullable= False, unique=True)
    password_hash = db.Column(db.String(), nullable= False)
    role = db.Column(db.String(), nullable=False)
    details = db.relationship('Detail', backref='user_referred', lazy=True)

    @property
    def password(self):
        return self.password


    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    # function to check if the password entered by the user matches its password in db
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def get_id(self):
        return (self.user_id)


# Detail table containing details of the employee with user_id as foreign key.
class Detail(db.Model):
    __tablename__ = 'detail'
    employeeID = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(length=30), nullable=False)
    last_name = db.Column(db.String(length=30), nullable=False)
    email = db.Column(db.String(length=50), nullable=False, unique=True)
    phone_no = db.Column(db.Integer(), nullable= False)
    dob = db.Column(db.Text(), nullable= False)
    address = db.Column(db.String(length=50), nullable= False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

