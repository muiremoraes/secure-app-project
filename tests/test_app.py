
import pytest
from app import app, init_db, get_db
import sqlite3

@pytest.fixture
def client():
    app.config["DATABASE"] = ":memory:" #in memeorry db 
    app.config["TESTING"] = True
    init_db() #create tables before runnign test
    client = app.test_client() #cretae test client
    return client


def test_register(client):
    res = client.post("/register", data={"username":"test", "password":"pass123"})
    assert res.status_code == 302


def test_register_with_same_name(client):
    client.post("/register", data={"username":"test", "password":"pass1234"})
    res = client.post("/register", data={"username":"test", "password":"pass123"})
    assert res.status_code == 302

def test_register_with_no_name(client):
    client.post("/register", data={"username":"", "password":"pass1234"})
    res = client.post("/register", data={"username":"", "password":"pass123"})
    assert res.status_code == 302

def test_register_with_no_password(client):
    client.post("/register", data={"username":"", "password":""})
    res = client.post("/register", data={"username":"", "password":""})
    assert res.status_code == 302
    

def test_register_with_no_name_or_password(client):
    client.post("/register", data={"username":"", "password":""})
    res = client.post("/register", data={"username":"", "password":""})
    assert res.status_code == 302


def test_login(client):
    client.post("/register", data={"username":"test", "password":"pass123"})
    res = client.post("/login", data={"username":"test", "password":"pass123"})
    assert res.status_code == 302


def test_login_with_invlaid_creds(client):
    client.post("/register", data={"username":"test", "password":"pass123"})
    res = client.post("/login", data={"username":"idk", "password":"pass"})
    assert res.status_code == 401

def test_login_no_username(client):
    client.post("/register", data={"username":"", "password":"pass123"})
    res = client.post("/login", data={"username":"", "password":"pass123"})
    assert res.status_code == 302


def test_login_no_password(client):
    client.post("/register", data={"username":"abc", "password":""})
    res = client.post("/login", data={"username":"abc", "password":""})
    assert res.status_code == 302


def test_login_no_password_or_username(client):
    client.post("/register", data={"username":"", "password":""})
    res = client.post("/login", data={"username":"", "password":""})
    assert res.status_code == 302

def test_note(client):
    client.post("/register", data={"username":"test", "password":"pass123"})
    client.post("/login", data={"username":"test", "password":"pass123"})
    client.post("/add_notes", data={"note_info":"blah blah something"})
    res = client.get("/notes")
    assert res.status_code == 200

def test_delete_note(client):
    client.post("/register", data={"username":"test", "password":"pass123"})
    client.post("/login", data={"username":"test", "password":"pass123"})
    client.post("/add_notes", data={"note_info":"blah blah something"})
    res = client.get("/delete/1")
    assert res.status_code == 302


# source ./venv/bin/activate
#  PYTHONPATH=. pytest -v -k "test"
