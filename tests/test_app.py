
import pytest
from app import app, init_db, get_db
import sqlite3

@pytest.fixture
def client():
    app.config["DATABASE"] = ":memory:"
    app.config["TESTING"] = True
    init_db()
    client = app.test_client()
    return client


def test_register(client):
    res = client.post("/register", data={"username":"test", "password":"pass123"})
    assert res.status_code == 302


def test_login(client):
    client.post("/register", data={"username":"test", "password":"pass123"})
    res = client.post("/login", data={"username":"test", "password":"pass123"})
    assert res.status_code == 302


def test_note(client):
    client.post("/register", data={"username":"test", "password":"pass123"})
    client.post("/login", data={"username":"test", "password":"pass123"})
    client.post("/add_notes", data={"note_info":"blah blah something"})
    res = client.get("/notes")
    assert res.status_code == 200