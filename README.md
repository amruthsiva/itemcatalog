# Candyshop Catalog
About:

This project is a RESTful web application utilizing the Flask framework which accesses a SQL database_setup that populates categories and their items. OAuth2 provides authentication for further CRUD functionality on the application. Currently OAuth2 is implemented for Google Accounts.

In This Repo:

This project has one main Python module application.py which runs the Flask application. A SQL database_setup is created using the database_setup.py module and you can populate the database_setup with test data using menu.py. The Flask application uses stored HTML templates in the tempaltes folder to build the front-end of the application. CSS are stored in the static directory.

Skills required:
1.Python

2.HTML

3.CSS

4.OAuth

5.Flask Framework

Installation:

There are some dependancies and a few instructions on how to run the application. Seperate instructions are provided to get GConnect working also


Setting up OAuth 2.0:

1.You will need to signup for a google account and set up a client id and secret

setup environment:

1.create a folder in that we store python files,html files in template folder,css files in static folder,json files,database_setup files.

2.open terminal in particular folder and create virtualenvironment then type virtualenv flask-env then flask environment will be created and flask-env activate then type source flask-env/bin/activate.

3.in that flask-env we install pip install Flask, pip install sqlalchemy,pip install oauth2clientand finally pip install requests.

4.we run the database_setup.py in terminal then database_setup.pyc and toffees.db will be created under the flask-env only.

5.we run the menu.py in terminal then added menu items in toffees.db will be created under the flask-env only.

6.run the main.py and the localhost:5000 will be running.

7.open webbrowser and type localhost:5000/login and login page will be opened.

8.then google sign with any account and its redirect to restaurants.

9.then show the Candyshops and Candys.

10.here we will add a new Candyshop (or) add a new Menu Item what ever we want.

11.And we want it to logout it then its redirect to showCandyshops.
