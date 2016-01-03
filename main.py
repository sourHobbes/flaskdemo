import sys
import os

from google.appengine.ext.db import BadRequestError

sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib'))
from flask import Flask, request, make_response
import time
import twilio.twiml
from google.appengine.ext import ndb

app = Flask(__name__)


def create_admin_user(user="admin", password="secret"):
    admin_user_key = ndb.Key("User", "admin")
    admin_user = admin_user_key.get()
    if not admin_user:
        user = User(user=user, pswd='secret', id=user)
        user.put()


class Lunch(ndb.Model):
    submitter = ndb.StringProperty()
    food = ndb.StringProperty()


class User(ndb.Model):

    '''
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    pswd = db.Column(db.String(100))
    '''
    user = ndb.StringProperty()
    pswd = ndb.StringProperty()

    @classmethod
    def _query(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key)


from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField

app.config["SECRET_KEY"] = 'secretkey'


class LunchForm(Form):
    submitter = StringField(u"Hi, my name is")
    food = StringField(u"and I ate")
    submit = SubmitField(u'share my lunch!')


'''
class UserLogin():
    def __init__(self, user, pswd, loginForm=None):
        if loginForm:
            try:
                self.user_name = loginForm.user_name.data
                self.pswd = loginForm.pswd.data
            except Exception, ex:
                raise AttributeError(ex.message)
        self.user_name = StringField(user)
        self.pswd = StringField(pswd)
'''


class LoginForm(Form):
    user_name = StringField(u"User")
    pswd = StringField(u"Password")
    login = SubmitField(u"LogIn")


class SmsForm(Form):
    sms_msg = StringField(u"message")
    sms_no = StringField(u"phone_no")
    sms = SubmitField(u"SendText")


class Error:
    def __init__(self, msg):
        self.msg = msg


from flask import render_template


class IsValid:
    def __init__(self, cookie):
        if cookie:
            time_elapsed = time.time() - float(cookie)
            if time_elapsed <= 100:
                return
        raise AttributeError("Invalid session cookie.")


def render_lunches_page(set_cookie=False):
    lunchs = Lunch.query()
    lform = LunchForm()
    resp = make_response(render_template('index.html', form=lform, lunches=lunchs))
    resp.set_cookie('user_name', str(time.time()))
    return resp


@app.route(u"/logon", methods=[u'POST', u'GET'])
def logon():
    form = LoginForm()

    if form.validate_on_submit():
        user_key = ndb.Key("User", form.user_name.data or 'admin')
        user = None
        try:
            user = user_key.get()
            if not user:
                raise AttributeError("Invalid user name."
                                     " Such a user does not exist or the password is incorrect")
            if user.pswd == form.pswd.data:
                return render_lunches_page(set_cookie=True)
            else:
                raise AttributeError("Invalid user name."
                                     " Such a user does not exist or the password is incorrect")
        except AttributeError, ex:
            login = LoginForm()
            error = Error(ex.message)
            return render_template('login.html', login=login, error=error)
        except BadRequestError, ex:
            login = LoginForm()
            error = Error("Please specify a valid user name")
            return render_template('login.html', login=login, error=error)
    else:
        login = LoginForm()
        sms = SmsForm()
        error = Error("No inputs.")
        return render_template('login.html', login=login, sms=sms, error=error)


@app.route(u"/sms", methods=[u'GET', u'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""

    resp = twilio.twiml.Response()
    resp.message("Hello, Mobile Monkey")
    return str(resp)


@app.route(u'/new', methods=[u'POST'])
def new_lunch():
    cookie = request.cookies.get('user_name')
    try:
        IsValid(cookie)
    except AttributeError, ex:
        login = LoginForm()
        error = Error(ex.message)
        return render_template('login.html', login=login, error=error)

    form = LunchForm()
    if form.validate_on_submit():
        if form.food.data == "" or form.submitter.data == "":
            return render_lunches_page(set_cookie=True)
        lunch = Lunch(submitter=form.submitter.data, food=form.food.data)
        lunch.put()
    return render_lunches_page()


@app.route(u'/lunches', methods=[u'GET'])
def get_lunches():
    cookie = request.cookies.get('user_name')
    try:
        IsValid(cookie)
    except AttributeError, ex:
        login = LoginForm()
        error = Error(ex.message)
        return render_template('login.html', login=login, error=error)
    import json
    res = json.dumps([p.to_dict() for p in Lunch.query().fetch()])
    return res


@app.route("/")
def root():
    #Uncomment this line to empty data base
    #ndb.delete_multi(Lunch.query().fetch(keys_only=True))
    create_admin_user()
    login = LoginForm()
    sms = SmsForm()
    return render_template('login.html', login=login, sms=sms)
    # return render_template('index.html', form=form, lunches=lunchs)
'''
if __name__ == "__main__":
    create_admin_user()
    app.debug = True
    app.run(port=80)
'''
