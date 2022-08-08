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
    completed = db.Column(db.BOOLEAN, nullable=False)

    # debugging helper
    def __repr__(self):
        return f'<Todo {self.id} {self.description} {self.completed}>'

db.create_all()

# ################## Controllers #################### #

# this listens to the homepage
@app.route('/')
def index():
    #this render_template returns an index.html
    return render_template('index.html', data=Todo.query.order_by('id').all())     

# this listens to the create
@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    # handling exception (if commits fail)
    try:
        # description = request.form.get('description', '')
        description = request.get_json()['description']
        todo = Todo(description = description, completed = False)
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

# this listens to the on checked function
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    # error = False
    # body = {}
    # print('todo id is ' + todo_id)
    # print('complete status for id ' + todo_id + ' is' + request.get_json()['completed'])
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.add(todo)
        db.session.commit()
        # body['completed'] = todo.completed
    except:
        # error = True
        db.session.rollback()
        # print(sys.exc_info())
    finally:
        db.session.close()
    
    return redirect(url_for('index'))

    # if error:
    #     abort(400)
    # else:
    #     return jsonify(body)

# this listens to the deled button function
@app.route('/todos/<todo_id>/delete-todo', methods=['GET'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))

#######################################################

#always include this at the bottom of your code
if __name__ == '__main__':
   app.run(host="0.0.0.0", port=3000)