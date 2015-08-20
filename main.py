# --------------------------------------------------
#   APP     UniVerse v0.0.1
#   AUTHOR  David Leger
#   DATE    August, 2015 
# --------------------------------------------------

# import Flask dependancies
from flask import Flask, render_template, flash, request, url_for, redirect, session

# import other dependancies
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as sanitize

#import custom scripts
from db_connect import connection

app = Flask(__name__)
app.secret_key = 'many random bytes'

# --------------------------------------------------
#   SECTION Define Routes & Templates
# --------------------------------------------------

# HOME
@app.route('/')
def home():
    try:
        return render_template("pages/home.html")
    
    except Exception as e:
        #flash(e)
        return str(e)
# --------------------------------------------------

# LOGIN
@app.route('/login/', methods = ['GET', 'POST'])
def login():
    
    error = "Hey"
    
    
    try:
        if request.method == "POST":
            attempted_username = request.form['login-email']
            attempted_password = request.form['login-password']
            
            flash(attempted_username)
            flash(attempted_password)
            
            if attempted_username == "dleger" and attempted_password == "password":
                return redirect(url_for('home'))
            else:
                error = "Username or password was incorrect. Please try again."
                
        return render_template("pages/login.html", error = error)
         
        
    except Exception as e:
        flash(e)
        error = "Failed."
    
    return render_template("pages/login.html", error = error)

# --------------------------------------------------

# REGISTER
# initialize register form fields and constraints
class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=32)])
    email = TextField('Email', [validators.Length(min=6, max=64)])
    password = PasswordField('Password', [validators.Required(),
                                          validators.EqualTo('confirm', 
                                                             message="Passwords do not match.")])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('Accept Terms of Service and Privacy Policy', [validators.Required()])
    

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    try:
        form = RegistrationForm(request.form)
        
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt(str(form.password.data))
            
            c, conn = connection()
            x = c.execute("SELECT * FROM users WHERE username = (%s)", 
                          [sanitize(username)])
            
            if int(x) > 0:
                flash("Username taken.")
                return render_template('pages/register.html', form = form)
            else:
                c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                         [sanitize(username), sanitize(password), sanitize(email)])
                conn.commit()
                c.close()
                conn.close()
                #gc.collect()
                
                flash("You are now Registered!")
                
                session['logged_in'] = True
                session['username'] = username
                
                return redirect(url_for('home'))
                
        return render_template('pages/register.html', form = form)
    except Exception as e:
        flash(e)
        return(str(e))
# --------------------------------------------------


# --------------------------------------------------
#   ERROR HANDLING PAGES
# --------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("err/404.html")

@app.errorhandler(405)
def page_not_found(e):
    return render_template("err/405.html")

@app.errorhandler(500)
def page_not_found(e):
    flash(str(e))
    return render_template("err/500.html")

if __name__=="__main__":
    app.run()