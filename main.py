from flask import Flask, request, render_template, url_for, redirect, sessions
from flask_sqlalchemy import SQLAlchemy
import re
app = Flask(__name__)

app.config['DEBUG'] = True
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://knitting:password@localhost:8889/knitting'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    yarns = db.relationship('Yarn', backref='user')
    #i need to connect these all to the backref- what is the process for this if i want to 
    #connect more than one table?

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Yarn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    yarn_brand = db.Column(db.String(1200))
    yarn_details= db.Column(db.String(1200))
    yarn_weight= db.Column(db.String(200))
    yarn_length= db.Column(db.String(200))
    yarn_color= db.Column(db.String(600))
    yarns = db.relationship('Yarn', backref='user')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, yarn_brand, yarn_details,yarn_weight, yarn_length, yarn_color, yarn_skeins, user):
        self.yarn_brand = yarn_brand
        self.yarn_details = yarn_details
        self.yarn_weight = yarn_weight
        self.yarn_length = yarn_length
        self.yarn_color = yarn_color
        self.yarn_skeins = yarn_skeins
        self.user = user

class Patterns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pattern_name = db.Column(db.String(1200))
    pattern_directions = db.Column(db.String(12000000))
    yarns = db.relationship('Yarn', backref='user')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, pattern_name, user):
        self.pattern_name = pattern_name
        self.user = user

@app.before_request
def require_login():
    allowed_routes=['login', 'blogs', 'create_username', 'index', 'logout']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')    


@app.route('/')
def index():
    return render_template('index.html')

def username_test(username):
    if username == "":
         return "blank_error"
    elif re.search("^\s", username) != None:
        return "space_error"
    elif re.search("^.+\s", username) != None:
        return "space_error"
    
    elif re.match("^[a-zA-Z0-9]{3,20}$", username) == None:
        return "format_error"
    
    else:
        return ""
def password_test(password):
    if password == "":
        return "blank_error"
    elif re.search("^\s", password) != None:
        return "space_error"
    elif re.search("^.+\s", password) != None:
        return "space_error"
    elif re.match("^[a-zA-Z0-9]{3,20}$", password) == None:
        return "format_error"
    else:
        return ""
def verify_password_test(verify_password, password):
    if verify_password == "":
        return "blank_error"
    elif verify_password != password:
        return "format_error"
    else:
        return ""
def email_test(email):
    if email == "":
        return ""
    elif re.search("^\s", email) != None:
        return "space_error"
    elif re.search("^.+\s", email) != None:
        return "space_error"
    elif re.match("^\@", email):
        return "format_error"
    elif re.match("[^@]+@[^@]+\.[^@]", email) == None:
        return "atsign_error"
    
    elif re.match("^[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+\.[a-zA-Z]{3,20}", email) == None:
        return "format_error"
    
    
    else:
        return ""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('name')
        password = request.form.get('password')
        member = User.query.filter_by(username=username).first()
        if member and password == member.password:
            session['username'] = username
            return redirect('/newposts')
        else:
            if not member:
                return render_template('home.html', registered_username=username, registered_username_error="Username does not exist")

            else:
                return render_template('home.html', registered_username=username, stored_password_error="Invalid Password" )
    else:
        return render_template('home.html')

@app.route('/createusername', methods=['GET','POST'])
def create_username():
    if request.method == "POST":
        username = request.form.get("username")
        already_exists = User.query.filter_by(username=username).first()
        password = request.form.get("password_entered")
        verify_password = request.form.get("verifypassword_entered")
        email = request.form.get("email_input")
        u_test = username_test(username) 
        p_test = password_test(password)
        pv_test = verify_password_test(verify_password, password)
        e_test = email_test(email)
        if already_exists:
            return render_template('createusername.html', username = username, email = email,  username_error = "already_exists", password_error = p_test, verify_error = pv_test, email_error = e_test)
        elif u_test != "" or p_test != "" or pv_test !="" or e_test != "":
            return render_template('createusername.html', username = username, email = email,  username_error = u_test, password_error = p_test, verify_error = pv_test, email_error = e_test)
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newposts')
    #need to add this info to the database
    else:

        return render_template('createusername.html')



def yarn_name_validate(name):
    if name == "":
        return "Please enter a brand of your yarn"
    else:
        return ""

def yarn_details_validate(content):
    if content == "":
        return "Please enter the details of your yarn"
    else:
        return ""

@app.route('/yarninfo', methods=['GET', 'POST'])
def yarn_details():
    if request.method == 'POST':
        blog_name = request.form.get('name')
        blog_body = request.form.get('content')
        if blog_name_validate(blog_name) or blog_body_validate(blog_body) != "":
            return render_template('newposts.html', title="Add a blog", title_error=blog_name_validate(blog_name), content_error=blog_body_validate(blog_body), old_name=blog_name, old_post=blog_body)
        else:
            new_blog = Blog(blog_name, blog_body, User.query.filter_by(username=session['username']).first())
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blogs?id=' + str(new_blog.id))
    else:
        return render_template("yarn_info.html", title="Add a purchased yarn")


#@app.route('/', methods=['GET', 'POST'])
#def index():
    #session['preload'] = "preload"
    #members = User.query.all()
    #return render_template('index.html', members=members)
    #del session['preload']

@app.route('/logout')
def logout():
    if 'username' in session:
        del session['username']
    return redirect('/blogs')


if __name__ == '__main__':
    app.run()