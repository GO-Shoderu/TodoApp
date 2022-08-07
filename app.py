from crypt import methods
from typing import final
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
import sys
from flask_sqlalchemy import SQLAlchemy

# by specfying __name__ it creates the app and names it after the name of the file
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/todoapp'
db = SQLAlchemy(app)

# this has some side effects
# db = SQLAlchemy(app, session_options={"expire_on_commit": False})

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)

    # debugging helper
    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

db.create_all()

# ################## Controllers #################### #

# this listens to the homepage
@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())     #this render_template returns an index.html

# this listens to the create
@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    # handling exception (if commits fail)
    try:
        # description = request.form.get('description', '')
        description = request.get_json()['description']
        todo = Todo(description = description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)
        
        # return redirect(url_for('index'))
        # return description + ' Todo Created!!!'

#######################################################

#always include this at the bottom of your code
if __name__ == '__main__':
   app.run(host="0.0.0.0", port=3000)