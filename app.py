import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# In-memory storage for todos
todos = []

class Todo:
    def __init__(self, title, description=""):
        self.id = str(uuid.uuid4())
        self.title = title.strip()
        self.description = description.strip()
        self.completed = False
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update(self, title=None, description=None, completed=None):
        if title is not None:
            self.title = title.strip()
        if description is not None:
            self.description = description.strip()
        if completed is not None:
            self.completed = completed
        self.updated_at = datetime.now()

def find_todo_by_id(todo_id):
    """Find a todo by its ID"""
    for todo in todos:
        if todo.id == todo_id:
            return todo
    return None

def get_filtered_todos(filter_type='all'):
    """Get todos based on filter type"""
    if filter_type == 'active':
        return [todo for todo in todos if not todo.completed]
    elif filter_type == 'completed':
        return [todo for todo in todos if todo.completed]
    else:  # 'all'
        return todos

@app.route('/')
def index():
    """Main page showing all todos"""
    filter_type = request.args.get('filter', 'all')
    filtered_todos = get_filtered_todos(filter_type)
    
    # Sort todos by creation date (newest first)
    filtered_todos.sort(key=lambda x: x.created_at, reverse=True)
    
    return render_template('index.html', 
                         todos=filtered_todos, 
                         current_filter=filter_type,
                         total_count=len(todos),
                         active_count=len([t for t in todos if not t.completed]),
                         completed_count=len([t for t in todos if t.completed]))

@app.route('/add', methods=['POST'])
def add_todo():
    """Add a new todo"""
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Task title is required!', 'error')
        return redirect(url_for('index'))
    
    if len(title) > 200:
        flash('Task title must be less than 200 characters!', 'error')
        return redirect(url_for('index'))
    
    # Create new todo
    new_todo = Todo(title, description)
    todos.append(new_todo)
    
    flash(f'Task "{title}" added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<todo_id>', methods=['POST'])
def toggle_todo(todo_id):
    """Toggle completion status of a todo"""
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        flash('Task not found!', 'error')
        return redirect(url_for('index'))
    
    todo.update(completed=not todo.completed)
    status = 'completed' if todo.completed else 'active'
    flash(f'Task marked as {status}!', 'success')
    
    return redirect(url_for('index', filter=request.form.get('filter', 'all')))

@app.route('/delete/<todo_id>', methods=['POST'])
def delete_todo(todo_id):
    """Delete a todo"""
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        flash('Task not found!', 'error')
        return redirect(url_for('index'))
    
    todos.remove(todo)
    flash(f'Task "{todo.title}" deleted successfully!', 'success')
    
    return redirect(url_for('index', filter=request.form.get('filter', 'all')))

@app.route('/edit/<todo_id>', methods=['POST'])
def edit_todo(todo_id):
    """Edit an existing todo"""
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        flash('Task not found!', 'error')
        return redirect(url_for('index'))
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Task title is required!', 'error')
        return redirect(url_for('index'))
    
    if len(title) > 200:
        flash('Task title must be less than 200 characters!', 'error')
        return redirect(url_for('index'))
    
    todo.update(title=title, description=description)
    flash(f'Task updated successfully!', 'success')
    
    return redirect(url_for('index', filter=request.form.get('filter', 'all')))

@app.route('/clear-completed', methods=['POST'])
def clear_completed():
    """Delete all completed todos"""
    global todos
    completed_todos = [todo for todo in todos if todo.completed]
    todos = [todo for todo in todos if not todo.completed]
    
    count = len(completed_todos)
    if count > 0:
        flash(f'{count} completed task(s) cleared!', 'success')
    else:
        flash('No completed tasks to clear!', 'info')
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html', todos=[], error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('index.html', todos=[], error="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
