
from flask import Flask, request, redirect, session, render_template
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret_key_shsjkwdsdiwuerfiweufh3382923DSCJKSDCJeoiosdifj5443"
csrf = CSRFProtect(app)

@app.after_request
def secure_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


class NameForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class NoteForm(FlaskForm):
    note_info = TextAreaField("Note", validators=[DataRequired()])
    submit = SubmitField("Submit")

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # create users table if not there
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    # create notes table if not there
    cur.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, user_id INTEGER, note_info TEXT)")

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row 
    return conn


init_db()
    
@app.route("/")
def get_login_page():
    return render_template("index.html")



@app.route("/register", methods=["GET","POST"])
def register():
    form = NameForm()
    if request.method == "POST":
        

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            conn = get_db()
            cur = conn.cursor()

            cur.execute("SELECT * FROM users WHERE username=(?)",(username,))
            if cur.fetchone():
                conn.close()
                return render_template("register.html", form=form, error="username is not cool enough")

            if len(username)< 8:
                conn.close()
                return render_template("register.html", form=form, error="usernames must be 8 long to be cool")

            if len(password) < 8:
                conn.close()
                return render_template("register.html", form=form, error="password must be at least 8 char long")

            if not any(char.isdigit() for char in password):
                conn.close()
                return render_template("register.html", form=form, error="password must be at least 1 number")
            
            if not any(char.isupper() for char in password):
                conn.close()
                return render_template("register.html", form=form, error="password must be at least 1 capital")

            if not any(char.islower() for char in password):
                conn.close()
                return render_template("register.html", form=form, error="password must be at least 1 lowercase")

            hash_pass = generate_password_hash(password)

            
            cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,hash_pass))

            conn.commit()
            conn.close()

            return redirect("/login")
        
    return render_template("register.html", form=form)
    

fake_pass = generate_password_hash("PasswordP1234")
@app.route("/login", methods=["GET","POST"])
def login():
    form = NameForm()
    if request.method == "POST":
        

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            conn = get_db()
            cur = conn.cursor()

            
            cur.execute("SELECT * FROM users WHERE username=(?)",(username,))

            user = cur.fetchone()
            conn.close()

            if user:
                hash_exist = user["password"]
            else:
                hash_exist= fake_pass
            
            check = check_password_hash(hash_exist,password)

            if user and check:
                session["user_id"] = user["id"]
                return redirect("/notes")
            else:
                return render_template("login.html", form=form, error="login failed")
    
    return render_template("login.html", form=form)



@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login")



@app.route("/add_notes", methods=["POST", "GET"])
def add_note():
    if "user_id" not in session:
        return redirect("/login")

    form = NoteForm()

    if form.validate_on_submit():
        note_txt = form.note_info.data


        conn = get_db()
        cur = conn.cursor()

        cur.execute("INSERT INTO notes (user_id, note_info) VALUES (?,?)",(session["user_id"],note_txt))
        conn.commit()
        conn.close()
        return redirect("/notes")

    return render_template("notes.html",form=form)



@app.route("/notes", methods=["GET"])
def view():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM notes WHERE user_id=(?)",(session["user_id"],))
    notes = cur.fetchall()
    conn.close()

    form = NoteForm()
    return render_template("notes.html",notes=notes, form=form)



@app.route("/delete/<id>", methods=["GET"])
def delete(id):
    
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM notes WHERE id=(?)",(id,))
    conn.commit()
    conn.close()
    return redirect("/notes")




if __name__ == "__main__":
    app.run(debug=True)








