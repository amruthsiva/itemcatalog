from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Candyshop, Candy, User


# Import Login session
from flask import session as login_session
import random
import string

# imports for gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# import login decorator
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "item catalog"

engine = create_engine('sqlite:///toffees.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Helper Functions
def createUser(login_session):
    session = DBSession()
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    session.close()
    return user.id


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    return user


def getUserID(email):
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).first()
        session.close()
        return user.id
    except:
        return None


def login_required(f):
    session = DBSession()

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_name' not in login_session:
            session.close()
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route('/login')
def showlogin():
    session = DBSession()
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits)for x in xrange(32))
    login_session['state'] = state
    session.close()
    return render_template('login.html', STATE=state)


# DISCONNECT - Revoke a current user's token and reset their login_session.
@app.route('/gdisconnect')
def gdisconnect():
    session = DBSession()
    # only disconnect a connected User
    access_token = login_session.get('access_token')
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print'Access Token is None'
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        session.close()
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is'
    print result
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gconnect', methods=['POST'])
def gconnect():
    session = DBSession()
    # validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application-json'
        session.close()
        return response
    # Obtain authorization code
    code = request.data

    try:
        # upgrade the authorization code in credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application-json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode("utf-8"))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Access token within the app
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    response = make_response(json.dumps('Succesfully connected users', 200))

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists or if it doesn't make a new one
    print 'User email is' + str(login_session['email'])
    user_id = getUserID(login_session['email'])
    if user_id:
        print 'Existing user#' + str(user_id) + 'matches this email'
    else:
            user_id = createUser(login_session)
            print 'New user_id#' + str(user_id) + 'created'
            login_session['user_id'] = user_id
            print 'Login session is tied to :id#' + str(
                login_session['user_id'])

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:150px;- \
      webkit-border-radius:150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/logout')
def logout():
    session = DBSession()
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
            flash("you have succesfully been logout")
            session.close()
            return redirect(url_for('showCandyshops'))
        else:
                flash("you were not logged in")
                return redirect(url_for('showCandyshops'))


# Show all candyshops

@app.route('/candyshop/')
def showCandyshops():
    session = DBSession()
    candyshops = session.query(Candyshop).all()
    # return "This page will show all my candyshops"
    session.close()
    return render_template('candyshops.html', candyshops=candyshops)


# Create a new candyshop
@app.route('/candyshop/new/', methods=['GET', 'POST'])
def newCandyshop():
    session = DBSession()
    if 'username' not in login_session:  
        return redirect('/login')
    if request.method == 'POST':
        newCandyshop = Candyshop(
            name=request.form['name'])
        session.add(newCandyshop)
        flash('New Candyshop %s Successfully Created' % newCandyshop.name)
        session.commit()
        session.close()
        return redirect(url_for('showCandyshops'))
    else:
        return render_template('newCandyshop.html')

# Delete a candyshop


@app.route('/candyshop/<int:candyshop_id>/delete/', methods=['GET', 'POST'])
def deleteCandyshop(candyshop_id):
    session = DBSession()
    candyshopToDelete = session.query(
        Candyshop).filter_by(id=candyshop_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session.delete(candyshopToDelete)
        flash('%s Successfully Deleted' % candyshopToDelete.name)
        session.commit()
        session.close()
        return redirect(
            url_for('showCandyshops', candyshop_id=candyshop_id))
    else:
        return render_template(
            'deleteCandyshop.html', candyshop=candyshopToDelete)
    # return 'This page will be for deleting candyshop %s' % candyshop_id

# Edit a candyshop


@app.route('/candyshop/<int:candyshop_id>/edit/', methods=['GET', 'POST'])
def editCandyshop(candyshop_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    editedCandyshop = session.query(
        Candyshop).filter_by(id=candyshop_id).one()
    if request.method == 'POST':
            editedCandyshop.name = request.form['name']
            session.add(editedCandyshop)
            flash('Candyshop Successfully Edited %s' % request.form['name'])
            session.commit()
            session.close()
            return redirect(url_for('showCandyshops'))
    else:
        return render_template('editCandyshop.html',
                               candyshop=editedCandyshop)

    # return 'This page will be for editing candyshop %s' % candyshop_id


# Show a candyshop menu
@app.route('/candyshop/<int:candyshop_id>/')
@app.route('/candyshop/<int:candyshop_id>/menu/')
def showMenu(candyshop_id):
    session = DBSession()
    candyshop = session.query(Candyshop).filter_by(id=candyshop_id).one()
    items = session.query(Candy).filter_by(
        candyshop_id=candyshop_id).all()
    session.close()
    return render_template('menu.html', items=items, candyshop=candyshop)
    # return 'This page is the menu for candyshop %s' % candyshop_id

# Create a new menu item


@app.route('/candyshop/<int:candyshop_id>/menu/new/',
           methods=['GET', 'POST'])
def newCandy(candyshop_id):
    session = DBSession()
    if 'username' not in login_session:
        session.close()
        return redirect('/login')
    candyshop = session.query(Candyshop).filter_by(id=candyshop_id).one()
    if request.method == 'POST':
        newItem = Candy(name=request.form['name'],
                        description=request.form['description'],
                        price=request.form['price'],
                        course=request.form['course'],
                        candyshop_id=candyshop_id,
                        user_id=candyshop.user_id)
        session.add(newItem)
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showMenu', candyshop_id=candyshop_id))
    else:
        return render_template('newcandy.html', candyshop_id=candyshop_id)
    # return 'This page is for making a new menu item for candyshop %s'
    # %candyshop_id

# Delete a menu item


@app.route('/candyshop/<int:candyshop_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteCandy(candyshop_id, menu_id):
    session = DBSession()
    if 'username' not in login_session:
        session.close()
        return redirect('/login')
    candyshop = session.query(Candyshop).filter_by(id=candyshop_id).one()
    itemToDelete = session.query(Candy).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', candyshop_id=candyshop_id))
    else:
        return render_template('deleteCandy.html', item=itemToDelete)
    # return "This page is for deleting menu item %s" % menu_id

# Edit a menu items


@app.route('/candyshop/<int:candyshop_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editCandy(candyshop_id, menu_id):
    session = DBSession()
    if 'username' not in login_session:
        session.close()
        return redirect('/login')
    editedItem = session.query(Candy).filter_by(id=menu_id).one()
    candyshop = session.query(Candyshop).filter_by(id=candyshop_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', candyshop_id=candyshop_id))
    else:
        return render_template(
            'editcandy.html', candyshop_id=candyshop_id,
            menu_id=menu_id, item=editedItem)

    # return 'This page is for editing menu item %s' % menu_id


@app.route('/candyshop/<int:candyshop_id>/menu/JSON')
def candyshopMenuJSON(candyshop_id):
    session = DBSession()
    candyshop = session.query(Candyshop).filter_by(id=candyshop_id).one()
    items = session.query(Candy).filter_by(
        candyshop_id=candyshop_id).all()
    session.close()
    return jsonify(Candys=[i.serialize for i in items])


@app.route('/candyshop/<int:candyshop_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(candyshop_id, menu_id):
    session = DBSession()
    Menu_Item = session.query(Candy).filter_by(id=menu_id).one()
    session.close()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/candyshop/JSON')
def candyshopsJSON():
    session = DBSession()
    candyshops = session.query(Candyshop).all()
    session.close()
    return jsonify(candyshops=[r.serialize for r in candyshops])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
