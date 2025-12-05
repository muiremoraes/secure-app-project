
import pytest
from app import app, init_db, get_db
import sqlite3

@pytest.fixture
def client():
    app.config["DATABASE"] = ":memory:" #in memory DB  for testing
    app.config["TESTING"] = True #enable testing mode
    app.config["WTF_CSRF_ENABLED"] = False #disable csrf for testing
    init_db() # initalise DB
    client = app.test_client() #create test client
    yield client


def test_register(client):
    res = client.post("/register", data={"username":"TestUser1abcnewname", "password":"Password123abc"})
    assert res.status_code in (302,200) # 302 redirect if user successful 200 is user exists


def test_register_with_same_name(client):
    client.post("/register", data={"username":"TestUser1abc", "password":"Password1234"})
    res = client.post("/register", data={"username":"TestUser1abc", "password":"Password123"})
    assert res.status_code == 200 #returns to same page as registration failed

def test_register_with_invalid_name(client):
    client.post("/register", data={"username":"1", "password":"Password1234"})
    res = client.post("/register", data={"username":"1", "password":"Password123"})
    assert res.status_code == 200 # returns to same page as registration failed

def test_register_with_invalid_pass(client):
    client.post("/register", data={"username":"1234abcd12345", "password":"password1234"})
    res = client.post("/register", data={"username":"1234abcd12345", "password":"password123"})
    assert res.status_code == 200 #returns to same page a registration failed

def test_login(client):
    client.post("/register", data={"username":"TestUser1abc123123123", "password":"Password123abc"})
    res = client.post("/login", data={"username":"TestUser1abc123123123", "password":"Password123abc"})
    assert res.status_code == 302 # redirects to notes


def test_login_with_invlaid_creds(client): 
    client.post("/register", data={"username":"testABCDEF", "password":"pass123ABCDEF"})
    res = client.post("/login", data={"username":"idk", "password":"pass"})
    assert res.status_code == 200 # redirects to same page as login failed


def test_note(client):
    client.post("/register", data={"username":"test1test2test3testT", "password":"Password@pass123"})
    client.post("/login", data={"username":"test1test2test3testT", "password":"Password@pass123"})
    client.post("/add_notes", data={"note_info":"blah blah something"})
    res = client.get("/notes")
    assert res.status_code == 200 # redirects to same page as login failed

def test_delete_note(client):
    client.post("/register", data={"username":"test1test2test3testT", "password":"Password@pass123"})
    client.post("/login", data={"username":"test1test2test3testT", "password":"Password@pass123"})
    client.post("/add_notes", data={"note_info":"blah blah something"})
    res = client.get("/delete/1")
    assert res.status_code == 302 # redirects to notes as delete was successful
    

# source ./venv/bin/activate
#  PYTHONPATH=. pytest -v -k "test"
