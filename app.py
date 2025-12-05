
from flask import Flask, request, redirect, session, render_template
from flask_wtf import FlaskForm, CSRFProtect #flask-wtf for csrf protection
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash # used for secure pass hashing
from flask_wtf.csrf import CSRFError # used for handling CSRF error
import logging #logs actions

app = Flask(__name__)
app.secret_key = "secret_key_shsjkwdsdiwuerfiweufh3382923DSCJKSDCJeoiosdifj5443"
csrf = CSRFProtect(app) #CSRF protection for all forms

@app.after_request
def secure_headers(response): # secuirty headeder sent after every request
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains' # forces https

    response.headers['Content-Security-Policy'] = ("default-src 'self'; " "frame-ancestors 'none'; " "form-action 'self'; ")
    # only load resources from server, prevent embedding url on site and can only send form to site
    response.headers['X-Content-Type-Options'] = 'nosniff' # preveent content sniffing as that would let a user see the format of data
    response.headers['X-Frame-Options'] = 'SAMEORIGIN' # prevents malicous useing hiding links on page
    response.headers['X-XSS-Protection'] = '1; mode=block' #XSS filter
    return response

app.config.update( #session settings
    SESSION_COOKIE_SECURE=True, #sent over https
    SESSION_COOKIE_HTTPONLY=True, #prevents JS access to cookies
    SESSION_COOKIE_SAMESITE='Lax', # to prevent CSRF
    PERMANENT_SESSION_LIFETIME=600 # session expire in 10min
)

logging.basicConfig(filename="info.log", level=logging.INFO, format= "%(asctime)s | %(message)s")
# logs in info.log, format is time and message


class NameForm(FlaskForm): #name form
    username = StringField("Username", validators=[DataRequired()]) #checks username isnt empty
    password = StringField("Password", validators=[DataRequired()]) # checks password isnt empty
    submit = SubmitField("Submit")

class NoteForm(FlaskForm): # form for adding notes
    note_info = TextAreaField("Note", validators=[DataRequired()]) 
    submit = SubmitField("Submit")

def init_db(): #initalize DB
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # create users table if not there
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    # create notes table if not there
    cur.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, user_id INTEGER, note_info TEXT)")

    conn.commit()
    conn.close()


def get_db(): #
    conn = sqlite3.connect("database.db") #connect to DB
    conn.row_factory = sqlite3.Row #get columns by name
    return conn


init_db() # checks DB is ready
    
@app.route("/")
def get_login_page():
    return render_template("index.html") # loads main page


@app.errorhandler(CSRFError)
def handle_csrf_error(e): #handles CSRF token errors for expired session
    form = NameForm()
    return render_template("login.html", form=form, error="session expired") # redirects to login



@app.route("/register", methods=["GET","POST"])
def register():
    form = NameForm()
    if request.method == "POST": # checks method is POST
        

        if form.validate_on_submit(): #validate form
            username = form.username.data
            password = form.password.data

            conn = get_db() 
            cur = conn.cursor()

            cur.execute("SELECT * FROM users WHERE username=(?)",(username,)) #check if username already exists
            if cur.fetchone(): #if username exists
                conn.close() #close connection
                return render_template("register.html", form=form, error="username is not cool enough") 
                # return error message and render register page

            if len(username)< 8: #checks length is at least 8 characters
                conn.close()
                return render_template("register.html", form=form, error="usernames must be 8 long to be cool") #displays error on register page

            if len(password) < 8: #checks password is at least 8
                conn.close()
                return render_template("register.html", form=form, error="password must be at least 8 char long")

            if not any(char.isdigit() for char in password): #checks digit in password
                conn.close()
                return render_template("register.html", form=form, error="password must be at least 1 number")
            
            if not any(char.isupper() for char in password): #checks for one uppercase in password
                conn.close()
                return render_template("register.html", form=form, error="password must be at least 1 capital")

            if not any(char.islower() for char in password): #checks for one lowercase in password
                conn.close()
                return render_template("register.html", form=form, error="password must be at least 1 lowercase")

            hash_pass = generate_password_hash(password) # chashes password using import 

            
            cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,hash_pass)) # add username and hashed pass to DB

            conn.commit()
            conn.close()
            id = session.get("user_id") #get user id from session
            logging.info(f"User registered: {username}") #logs username that got registered

            return redirect("/login") # redirect to login 
        
    return render_template("register.html", form=form) # gets register page if any issues 
    

fake_pass = generate_password_hash("PasswordP1234") # fake password hashed to prevent timing attacks
@app.route("/login", methods=["GET","POST"])
def login():
    form = NameForm()
    if request.method == "POST": #checks method is post
        

        if form.validate_on_submit(): # validates form
            username = form.username.data
            password = form.password.data

            conn = get_db()
            cur = conn.cursor()

            
            cur.execute("SELECT * FROM users WHERE username=(?)",(username,)) # gets user with that username 

            user = cur.fetchone()
            conn.close()

            if user: #if user exist use real password
                hash_exist = user["password"]
            else:
                hash_exist= fake_pass
            
            check = check_password_hash(hash_exist,password) #compare hashes 

            if user and check: # if login succesful 
                session.clear() # clear old session
                session.permanent = True # make session equal session lifetime whihc is 10min
                session["user_id"] = user["id"] #store user id in session
                logging.info(f"User logged in: {username}") #log action 
                return redirect("/notes")
            else:
                logging.info(f"User login failed: {username}") # log error
                return render_template("login.html", form=form, error="login failed") #redirect to login page and display error message
    
    return render_template("login.html", form=form) 



@app.route("/logout", methods=["GET"]) #logout fucntion
def logout():
    id = session.get("user_id") # get current user id from session
    logging.info(f"User logged out id={id}") #log user id and action
    session.clear() # clear session
    return redirect("/login") #redirect to login



@app.route("/add_notes", methods=["POST", "GET"])
def add_note():
    if "user_id" not in session: #checks if user is still in session
        return redirect("/login") #else redirects to login page


    form = NoteForm()

    if form.validate_on_submit(): #validate note info
        note_txt = form.note_info.data


        conn = get_db()
        cur = conn.cursor()
        #add note into notes into table with user id.
        cur.execute("INSERT INTO notes (user_id, note_info) VALUES (?,?)",(session["user_id"],note_txt))
        conn.commit()
        conn.close()
        id = session.get("user_id") #get user id from session
        logging.info(f"User added note, id={id}") #log action with id
        return redirect("/notes") #redirects to notes

    return render_template("notes.html",form=form) #if not valid note or request render notes page



@app.route("/notes", methods=["GET"])
def view():
    if "user_id" not in session: #checks if user is logged in
        return redirect("/login") #else redirects to login

    conn = get_db()
    cur = conn.cursor()

    #get all notes from notes that belong to that user id
    cur.execute("SELECT * FROM notes WHERE user_id=(?)",(session["user_id"],))
    notes = cur.fetchall() # get all notes that meet that request
    conn.close()

    form = NoteForm() #form on page for adding notes
    return render_template("notes.html",notes=notes, form=form)



@app.route("/delete/<id>", methods=["GET"]) # delete note by id 
def delete(id):
    
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM notes WHERE id=(?)",(id,)) #delete from notes based on id
    conn.commit()
    conn.close()
    id = session.get("user_id") # get id from session 
    logging.info(f"User deleted note, id={id}") #logs deleted note and id
    return redirect("/notes")




if __name__ == "__main__":
    app.run(debug=False)
# debug flase so if an error happens no stack trace







