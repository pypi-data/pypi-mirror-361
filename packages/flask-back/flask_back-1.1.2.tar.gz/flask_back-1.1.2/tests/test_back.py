import pytest
from flask import Flask, session, redirect, render_template_string
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from flask_back import Back


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "test"
    back = Back()
    back.init_app(app, excluded_endpoints={"excluded"}, default_url="/fallback", use_referrer=True, back_url="/go-back")

    @app.route("/save")
    @back.save_url
    def save():
        return "saved"

    @app.route("/go-back")
    @back.exclude
    def go_back():
        return redirect(back.get_url())

    @app.route("/excluded")
    @back.exclude
    def excluded():
        return "excluded"

    return app


@pytest.fixture
def client(app):
    return app.test_client()


# === Core behavior tests ===

def test_save_url(client):
    res = client.get("/save")
    assert res.status_code == 200
    with client.session_transaction() as sess:
        assert sess["back_url"].endswith("/save")


def test_get_back_url(client):
    client.get("/save")
    res = client.get("/go-back", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/save")


def test_excluded_endpoint(client):
    client.get("/excluded")
    with client.session_transaction() as sess:
        assert "back_url" not in sess


def test_get_url_with_referrer(client):
    res = client.get("/go-back", headers={"Referer": "/referrer"}, follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/referrer")


def test_get_url_with_fallback(client):
    res = client.get("/go-back", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/fallback")


def test_template_injection(client, app):
    back = app.extensions["back"]

    @app.route("/template-test")
    @back.exclude
    def template_test():
        return render_template_string("Back to: {{ back_url }}")

    with client:
        client.get("/save")
        res = client.get("/template-test")
        assert b"/save" in res.data


# === Coverage-focused tests ===

def test_init_with_app():
    app = Flask(__name__)
    app.secret_key = "test"
    back = Back(app, default_url="/init")
    assert app.extensions["back"] is back


def test_before_request_skips_non_get(client):
    res = client.post("/save")
    with client.session_transaction() as sess:
        assert "back_url" not in sess


def test_before_request_skips_static(client):
    client.get("/static/file.js")
    with client.session_transaction() as sess:
        assert "back_url" not in sess


def test_clear_method(client, app):
    client.get("/save")
    with client.session_transaction() as sess:
        assert "back_url" in sess
    back = app.extensions["back"]
    with app.test_request_context("/"):
        back.clear()
        assert "back_url" not in session



def test_home_url_injection_none(client, app):
    back = app.extensions["back"]
    back._home_urls = ["/home"]

    @app.route("/home")
    def home():
        return render_template_string("Back URL: {{ back_url }}")

    with client:
        client.get("/save")
        res = client.get("/home")
        assert b"Back URL: None" in res.data


def test_dynamic_go_back_route():
    app = Flask(__name__)
    app.secret_key = "test"
    back = Back(app, back_url=True)

    @app.route("/set")
    def set_back():
        session["back_url"] = "/set"
        return "ok"

    client = app.test_client()
    client.get("/set")
    res = client.get("/go-back", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/set")
    
    
def test_before_request_skips_go_back():
    app = Flask(__name__)
    app.secret_key = "test"
    back = Back(app, back_url=True)

    @app.route("/set")
    def set_back():
        session["back_url"] = "/from-set"
        return "ok"

    client = app.test_client()
    client.get("/set")
    client.get("/go-back")  # should not overwrite back_url
    with client.session_transaction() as sess:
        assert sess["back_url"] == "/from-set"


def test_before_request_skips_home_url(client, app):
    back = app.extensions["back"]
    back._home_urls = ["/home"]

    @app.route("/home")
    def home():
        return "home"

    client.get("/home")
    with client.session_transaction() as sess:
        assert "back_url" not in sess

def test_before_request_saves_referrer_if_different(client, app):
    @app.route("/page")
    def page():
        return "ok"

    res = client.get("/page", headers={"Referer": "http://localhost/prev"})
    with client.session_transaction() as sess:
        assert sess["back_url"] == "/prev"


def test_skip_saving_on_go_back_path():
    app = Flask(__name__)
    app.secret_key = "test"
    back = Back(app, back_url=True)  # creates /go-back route automatically

    @app.route("/page")
    def page():
        session["back_url"] = "/page"
        return "page"

    client = app.test_client()
    client.get("/page")

    # Do not decorate /go-back manually. Let Back handle it.
    res = client.get("/go-back")
    assert res.status_code == 302

    with client.session_transaction() as sess:
        assert sess["back_url"] == "/page"  # not overwritten


def test_save_url_when_referrer_differs(client, app):
    @app.route("/current")
    def current():
        return "current"

    # referrer is /previous, path is /current — they differ
    client.get("/current", headers={"Referer": "http://localhost/previous"})

    with client.session_transaction() as sess:
        assert sess["back_url"] == "/previous"

