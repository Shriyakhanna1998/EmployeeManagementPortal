import datetime, flask_login, jwt

from Employee import app
from flask import render_template, request, flash, redirect, url_for, jsonify, session
from flask_restful import Api, Resource,abort, reqparse, fields, marshal_with
from Employee.models import User, Detail
from Employee import db
from flask_login import login_user, logout_user, login_required
from functools import wraps
from Employee.forms import CreateUser, RegistrationForm, LoginForm

api = Api(app)


@app.route('/')
def index():
    form = CreateUser()
    return render_template("index.html", form=form)


@app.route('/register', methods=["GET"])
def register():
    form = RegistrationForm()
    return render_template("registration_form.html", form = form)


@app.route('/login')
def login():
    form = LoginForm()
    return render_template("login.html", form=form)


# Logging in the user with respective permission and role.
@app.route('/logging_in')
@login_required
def logging_in():
    flash(f"Welcome ! You are now logged in as {flask_login.current_user.username}", category='success')
    if flask_login.current_user.role == "employee":
        return redirect(url_for('employee_detail', user_id=flask_login.current_user.user_id))
    else:
        return redirect(url_for('employee_master'))


# Employee_detail route to view details of the employee
# Can be viewed by admin or the respective employee only
@app.route('/employee_detail/<user_id>')
@login_required
def employee_detail(user_id):
    res = Detail.query.filter_by(user_id=str(user_id)).first()
    if flask_login.current_user.user_id == int(user_id):
        if not res:
            flash("You have not filled any details. Ask Admin to fill your details.", category='info')
            return render_template("employee.html")
        else:
            return render_template("employee.html", fname=res.first_name, lname=res.last_name, email=res.email,
                                   phone_no=res.phone_no, dob=res.dob, address=res.address, user_id=res.user_id, Role="Employee")
    elif flask_login.current_user.role == "admin":
        if res:
            return render_template("employee.html", fname=res.first_name, lname=res.last_name, email=res.email,
                                       phone_no=res.phone_no, dob=res.dob, address=res.address, user_id=res.user_id, Role="Master")
        else:
            flash("Error! No employee exists with this id!", category='danger')
            return redirect(url_for('employee_master'))
    else:
        flash("You are not authorized to access the other employee's details!", category='danger')
        return redirect(url_for('employee_detail', user_id=flask_login.current_user.user_id))


# Master Screen route to view all user and also perform all the functionalities - by Admin Access only.
# Patch and Delete REST-Api can only be accessed by JWT token.
@app.route('/employee_master')
@login_required
def employee_master():
    data = Detail.query.all()
    # Checking for admin access
    if flask_login.current_user.role == "admin":
        return render_template("master.html", details=data)
    # In case employee tries to access this screen.
    flash("You are not authorized to access the Employee Master Screen!", category='danger')
    return redirect(url_for('employee_detail', user_id=flask_login.current_user.user_id ))


# Searching user based on their first_name, last_name and address -  Admin Access Only.
@app.route('/search/<tag>')
@login_required
def search_result(tag):
    obj = EmployeeSearch()
    res = obj.get(tag);
    # Checking for admin access
    if flask_login.current_user.role == "admin":
        # If there are no relevant results.
        if res == []:
            flash("No Results Found!", category='danger')
            return redirect(url_for('employee_master'))
        return render_template('master.html', details=res)
    # In case employee tries to access this screen.
    flash("You are not authorized to access the Employee Master Screen!", category='danger')
    return redirect(url_for('employee_detail', user_id=flask_login.current_user.user_id))


@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('index'))


# Verifying if token is present in Headers of the Api call.
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(user_id=data['user_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


# Accepting the manner in which the post api of class User will be receiving the arguments.
user_post_args = reqparse.RequestParser()
user_post_args.add_argument("username", type=str, help="Username of the user", required=True)
user_post_args.add_argument("password", type=str, help="Password of the user", required=True)
user_post_args.add_argument("role", type=str, help="Role of the user", required=True)


# Accepting the manner in which the patch api of class User will be receiving the arguments.
user_patch_args = reqparse.RequestParser()
user_patch_args.add_argument("username", type=str, help="Username of the user")
user_patch_args.add_argument("password", type=str, help="Password of the user")
user_patch_args.add_argument("role", type=str, help="Role of the user")

resource_fields= {
    'user_id': fields.Integer,
    'username': fields.String,
    'password_hash': fields.String,
    'role': fields.String
}


# shows a single item and lets you update and delete a user
class Users(Resource):

    @marshal_with(resource_fields)
    @token_required
    def get(self, current_user, id):
        result = User.query.filter_by(user_id = id).first()
        if not result:
            abort(404, message="Could not find the user with this id.")
        return result

    @marshal_with(resource_fields)
    def patch(self, id):
        args = user_patch_args.parse_args()
        result = User.query.filter_by(user_id = id).first()
        if not result:
            abort(404, message="Could not find the user with this id.")
        if args["username"]:
            result.username = args["username"]
        if args["password"]:
            result.password = args["password"]
        if args["role"]:
            result.role = args["role"]
        db.session.commit()

        return result

    @token_required
    def delete(self, current_user, id):
        result = User.query.filter_by(user_id=id).first()
        if not result:
            abort(404, message="Could not find the user with this user id")
        db.session.delete(result)
        db.session.commit()

        return '', 204


# shows a list of all users, and lets you POST to add new user
class UserList(Resource):

    @marshal_with(resource_fields)
    @token_required
    def get(self, current_user):
        result = User.query.all()
        return result

    @marshal_with(resource_fields)
    def post(self):
        args = user_post_args.parse_args()
        username = args["username"]
        password = args["password"]
        role = args["role"]
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return new_user


class UserName(Resource):

    @marshal_with(resource_fields)
    def get(self, username):
        result = User.query.filter_by(username= username).first()
        if not result:
            result = {
                "message":"Could not find the user with this username"
            }
            abort(404, message="Could not find the user with this username.")
        return result


# Verifies a user during a login attempt
# Accepts basic-authorization of username and password
# this can also be provided in login page.
# after verifying this attempt it generates a token for the particular user and also logs him/her in.
class Authenticate(Resource):

    def get(self):
        auth = request.authorization
        attempted_user = User.query.filter_by(username= auth.username).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=auth.password):
            login_user(attempted_user)
            token = jwt.encode({'user_id': attempted_user.user_id,
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
                               , app.config['SECRET_KEY']
                               )
            # Saving this token for future reference
            session["cookie"] = token.decode('utf-8')
            return jsonify({'token' : token.decode('utf-8'), 'role': attempted_user.role, 'key':1})
        return jsonify({'message': 'User does not exists','key': 0})


# REST-Apis related to table User
api.add_resource(UserList, "/user", endpoint = "user")
api.add_resource(Users, "/user/<int:id>")
api.add_resource(UserName, "/user/<string:username>", endpoint = "username")
api.add_resource(Authenticate, "/user/authenticate")


# Accepting the manner in which the post api of class Employee will be receiving the arguments.
detail_post_args = reqparse.RequestParser()
detail_post_args.add_argument("first_name", type=str, help="First name of the user", required=True)
detail_post_args.add_argument("last_name", type=str, help="Last name of the user", required=True)
detail_post_args.add_argument("email", type=str, help="Email Address of the user", required=True)
detail_post_args.add_argument("phone_no", type=str, help="Contact number of the user", required=True)
detail_post_args.add_argument("dob", type=str, help="Date of birth of the user", required=True)
detail_post_args.add_argument("address", type=str, help="Address of the user", required=True)


# Accepting the manner in which the patch api of class Employee will be receiving the arguments.
detail_patch_args = reqparse.RequestParser()
detail_patch_args.add_argument("first_name", type=str, help="First name of the user")
detail_patch_args.add_argument("last_name", type=str, help="Last name of the user")
detail_patch_args.add_argument("email", type=str, help="Email Address of the user")
detail_patch_args.add_argument("phone_no", type=str, help="Contact number of the user")
detail_patch_args.add_argument("dob", type=str, help="Date of birth of the user")
detail_patch_args.add_argument("address", type=str, help="Address of the user")


resource_detail = {
    'employeeID': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'phone_no': fields.Integer,
    'dob' : fields.String,
    'address': fields.String,
    'user_id': fields.Integer
}


# shows a details of all the users
class EmployeeList(Resource):

    @marshal_with(resource_detail)
    @token_required
    def get(self, current_user):
        result = Detail.query.all()
        return result


# shows a details of all the employee with specific user_id
class Employee(Resource):

    @marshal_with(resource_detail)
    @token_required
    def get(self, id):
        result = Detail.query.filter_by(user_id=id).first()
        return result

    @marshal_with(resource_detail)
    def post(self, id):
        args = detail_post_args.parse_args()
        dto = datetime.datetime.strptime(args["dob"], '%Y-%m-%d').date()
        new_user_detail = Detail(first_name=args["first_name"], last_name=args["last_name"], email=args["email"],
                                 phone_no=int(args["phone_no"]), dob = dto, address=args["address"], user_id= id)
        db.session.add(new_user_detail)
        db.session.commit()
        return new_user_detail

    @token_required
    def delete(self, current_user, id):
        result = Detail.query.filter_by(user_id=id).first()
        if not result:
            abort(404, message="Could not find the user with this user id")
        db.session.delete(result)
        db.session.commit()

        return '', 204

    @marshal_with(resource_detail)
    @token_required
    def patch(self, current_user, id):
        args = detail_patch_args.parse_args()
        result = Detail.query.filter_by(user_id = id).first()
        if not result:
            abort(404, message="Could not find the user with this id.")
        if args["first_name"]:
            result.first_name = args["first_name"]
        if args["last_name"]:
            result.last_name = args["last_name"]
        if args["email"]:
            result.email = args["email"]
        if args["phone_no"]:
            result.phone_no = args["phone_no"]
        if args["dob"]:
            result.dob = args["dob"]
        if args["address"]:
            result.address = args["address"]
        db.session.commit()

        return result


# Rest-ful search Api to search employee based on first_name, last_name and address.
class EmployeeSearch(Resource):

    @marshal_with(resource_detail)
    def get(self, s):
        c=0
        search = "%{}%".format(s)
        result = Detail.query.filter(Detail.first_name.like(search)).all()
        if not result:
            result = Detail.query.filter(Detail.last_name.like(search)).all()
        if not result:
            result = Detail.query.filter(Detail.address.like(search)).all()
        for r in result:
            if r.employeeID == 0:
                c +=1
        if c > 0:
            return {"message" : "No user found"}
        return result


# REST-Apis related to table Detail
api.add_resource(EmployeeList, "/employee")
api.add_resource(Employee, "/employee/<int:id>", endpoint="employee")
api.add_resource(EmployeeSearch, "/employee/<string:s>")
