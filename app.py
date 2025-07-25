import os
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from supabase.client import Client, create_client  # create_client는 여전히 유틸 함수로 제공됨 (v2.17 기준)


# Supabase 연결 정보 (본인 프로젝트 정보로 수정)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://qcbrfdohpgemzzlzfphx.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFjYnJmZG9ocGdlbXp6bHpmcGh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM0MzAyNjMsImV4cCI6MjA2OTAwNjI2M30.f5XyWFvyDdwRv-jZCXQ0JsEfJfpsq7PHrysQA2Tm9K4")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

def get_filtered_todos(filter_type='all'):
    if filter_type == 'active':
        res = supabase.table("todos").select("*").eq("is_complete", False).order("created_at", desc=True).execute()
    elif filter_type == 'completed':
        res = supabase.table("todos").select("*").eq("is_complete", True).order("created_at", desc=True).execute()
    else:
        res = supabase.table("todos").select("*").order("created_at", desc=True).execute()
    return res.data if res.data else []

def get_counts():
    all_todos = supabase.table("todos").select("*").execute().data or []
    active_count = len([t for t in all_todos if not t.get("is_complete")])
    completed_count = len([t for t in all_todos if t.get("is_complete")])
    return len(all_todos), active_count, completed_count

@app.route('/')
def index():
    filter_type = request.args.get('filter', 'all')
    todos = get_filtered_todos(filter_type)
    total_count, active_count, completed_count = get_counts()
    return render_template('index.html', 
                         todos=todos, 
                         current_filter=filter_type,
                         total_count=total_count,
                         active_count=active_count,
                         completed_count=completed_count)

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    if not title:
        flash('Task title is required!', 'error')
        return redirect(url_for('index'))
    if len(title) > 200:
        flash('Task title must be less than 200 characters!', 'error')
        return redirect(url_for('index'))
    data = {"title": title, "is_complete": False, "created_at": datetime.utcnow().isoformat()}
    supabase.table("todos").insert(data).execute()
    flash(f'Task "{title}" added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>', methods=['POST'])
def toggle_todo(todo_id):
    res = supabase.table("todos").select("is_complete").eq("id", todo_id).single().execute()
    if not res.data:
        flash('Task not found!', 'error')
        return redirect(url_for('index'))
    new_status = not res.data["is_complete"]
    supabase.table("todos").update({"is_complete": new_status}).eq("id", todo_id).execute()
    status = 'completed' if new_status else 'active'
    flash(f'Task marked as {status}!', 'success')
    return redirect(url_for('index', filter=request.form.get('filter', 'all')))

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    res = supabase.table("todos").delete().eq("id", todo_id).execute()
    if res.count == 0:
        flash('Task not found!', 'error')
    else:
        flash('Task deleted successfully!', 'success')
    return redirect(url_for('index', filter=request.form.get('filter', 'all')))

@app.route('/edit/<int:todo_id>', methods=['POST'])
def edit_todo(todo_id):
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    if not title:
        flash('Task title is required!', 'error')
        return redirect(url_for('index'))
    if len(title) > 200:
        flash('Task title must be less than 200 characters!', 'error')
        return redirect(url_for('index'))
    update_data = {"title": title}
    supabase.table("todos").update(update_data).eq("id", todo_id).execute()
    flash('Task updated successfully!', 'success')
    return redirect(url_for('index', filter=request.form.get('filter', 'all')))

@app.route('/clear-completed', methods=['POST'])
def clear_completed():
    res = supabase.table("todos").delete().eq("is_complete", True).execute()
    count = res.count or 0
    if count > 0:
        flash(f'{count} completed task(s) cleared!', 'success')
    else:
        flash('No completed tasks to clear!', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html', todos=[], error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html', todos=[], error="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
