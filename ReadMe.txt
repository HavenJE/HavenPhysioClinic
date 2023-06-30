To set up python virtual env.
python3.8 -m venv venv
source venv/bin/activate
pip3 install pip --upgrade
pip3 install flask
pip3 install flask-SQLAlchemy (if produces error => /bin/python3: can't find '__main__' module in), then try the method below:
pip3 install flask-SQLAlchemy==3.0.3
pip3 install flask_wtf flask_bootstrap email_validator install
# flask_sqlalchemy

To install SQLite on ubuntu follow:
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-sqlite-on-ubuntu-20-04
# sqlite3 ecommerce.db

To run the flask app:
- cd path/to/project
- source venv/bin/activate
- python3 app.py
- In a browser open http://127.0.0.1:5000/

