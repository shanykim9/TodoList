import os
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase 연결 정보
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://qcbrfdohpgemzzlzfphx.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFjYnJmZG9ocGdlbXp6bHpmcGh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM0MzAyNjMsImV4cCI6MjA2OTAwNjI2M30.f5XyWFvyDdwRv-jZCXQ0JsEfJfpsq7PHrysQA2Tm9K4")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase 연결 성공")
except Exception as e:
    logger.error(f"Supabase 연결 실패: {e}")
    supabase = None

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

def get_filtered_todos(filter_type='all'):
    if not supabase:
        flash('데이터베이스 연결에 실패했습니다.', 'error')
        return []
    
    try:
        if filter_type == 'active':
            res = supabase.table("todos").select("*").eq("is_complete", False).order("created_at", desc=True).execute()
        elif filter_type == 'completed':
            res = supabase.table("todos").select("*").eq("is_complete", True).order("created_at", desc=True).execute()
        else:
            res = supabase.table("todos").select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        logger.error(f"데이터 조회 실패: {e}")
        flash('데이터를 불러오는데 실패했습니다.', 'error')
        return []

def get_counts():
    if not supabase:
        return 0, 0, 0
    
    try:
        all_todos = supabase.table("todos").select("*").execute().data or []
        active_count = len([t for t in all_todos if not t.get("is_complete")])
        completed_count = len([t for t in all_todos if t.get("is_complete")])
        return len(all_todos), active_count, completed_count
    except Exception as e:
        logger.error(f"카운트 조회 실패: {e}")
        return 0, 0, 0

def format_korea_time(datetime_str):
    """한국 시간으로 포맷팅"""
    try:
        # UTC 시간을 한국 시간으로 변환
        utc_time = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        korea_timezone = timezone(timedelta(hours=9))
        korea_time = utc_time.astimezone(korea_timezone)
        return korea_time.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return datetime_str[:19].replace('T', ' ') if datetime_str else 'N/A'

@app.route('/')
def index():
    filter_type = request.args.get('filter', 'all')
    todos = get_filtered_todos(filter_type)
    
    # 시간 포맷팅 적용
    for todo in todos:
        if todo.get('created_at'):
            todo['created_at_formatted'] = format_korea_time(todo['created_at'])
        if todo.get('updated_at'):
            todo['updated_at_formatted'] = format_korea_time(todo['updated_at'])
    
    total_count, active_count, completed_count = get_counts()
    return render_template('index.html', 
                         todos=todos, 
                         current_filter=filter_type,
                         total_count=total_count,
                         active_count=active_count,
                         completed_count=completed_count)

@app.route('/add', methods=['POST'])
def add_todo():
    if not supabase:
        flash('데이터베이스 연결에 실패했습니다.', 'error')
        return redirect(url_for('index'))
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('작업 제목을 입력해주세요!', 'error')
        return redirect(url_for('index'))
    
    if len(title) > 200:
        flash('작업 제목은 200자 이하여야 합니다!', 'error')
        return redirect(url_for('index'))
    
    try:
        # 한국 시간으로 저장 (UTC + 9시간)
        korea_timezone = timezone(timedelta(hours=9))
        korea_time = datetime.now(korea_timezone)
        
        # 기본 데이터만 먼저 시도 (description 없이)
        data = {
            "title": title, 
            "is_complete": False, 
            "created_at": korea_time.isoformat()
        }
        
        supabase.table("todos").insert(data).execute()
        flash(f'작업 "{title}"이(가) 성공적으로 추가되었습니다!', 'success')
        
    except Exception as e:
        logger.error(f"작업 추가 실패: {e}")
        flash('작업 추가에 실패했습니다. 데이터베이스 설정을 확인해주세요.', 'error')
    
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>', methods=['POST'])
def toggle_todo(todo_id):
    if not supabase:
        flash('데이터베이스 연결에 실패했습니다.', 'error')
        return redirect(url_for('index'))
    
    try:
        res = supabase.table("todos").select("is_complete").eq("id", todo_id).single().execute()
        if not res.data:
            flash('작업을 찾을 수 없습니다!', 'error')
            return redirect(url_for('index'))
        
        new_status = not res.data["is_complete"]
        supabase.table("todos").update({"is_complete": new_status}).eq("id", todo_id).execute()
        status = '완료' if new_status else '진행중'
        flash(f'작업이 {status}로 표시되었습니다!', 'success')
    except Exception as e:
        logger.error(f"작업 상태 변경 실패: {e}")
        flash('작업 상태 변경에 실패했습니다.', 'error')
    
    return redirect(url_for('index', filter=request.form.get('filter', 'all')))

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    if not supabase:
        flash('데이터베이스 연결에 실패했습니다.', 'error')
        return redirect(url_for('index'))
    
    try:
        res = supabase.table("todos").delete().eq("id", todo_id).execute()
        if res.count == 0:
            flash('작업을 찾을 수 없습니다!', 'error')
        else:
            flash('작업이 성공적으로 삭제되었습니다!', 'success')
    except Exception as e:
        logger.error(f"작업 삭제 실패: {e}")
        flash('작업 삭제에 실패했습니다.', 'error')
    
    return redirect(url_for('index', filter=request.form.get('filter', 'all')))

@app.route('/edit/<int:todo_id>', methods=['POST'])
def edit_todo(todo_id):
    if not supabase:
        flash('데이터베이스 연결에 실패했습니다.', 'error')
        return redirect(url_for('index'))
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('작업 제목을 입력해주세요!', 'error')
        return redirect(url_for('index'))
    
    if len(title) > 200:
        flash('작업 제목은 200자 이하여야 합니다!', 'error')
        return redirect(url_for('index'))
    
    try:
        # title만 업데이트 (description 제외)
        update_data = {"title": title}
        supabase.table("todos").update(update_data).eq("id", todo_id).execute()
        flash('작업이 성공적으로 수정되었습니다!', 'success')
        
    except Exception as e:
        logger.error(f"작업 수정 실패: {e}")
        flash('작업 수정에 실패했습니다.', 'error')
    
    return redirect(url_for('index', filter=request.form.get('filter', 'all')))

@app.route('/clear-completed', methods=['POST'])
def clear_completed():
    if not supabase:
        flash('데이터베이스 연결에 실패했습니다.', 'error')
        return redirect(url_for('index'))
    
    try:
        res = supabase.table("todos").delete().eq("is_complete", True).execute()
        count = res.count or 0
        if count > 0:
            flash(f'{count}개의 완료된 작업이 삭제되었습니다!', 'success')
        else:
            flash('삭제할 완료된 작업이 없습니다!', 'info')
    except Exception as e:
        logger.error(f"완료된 작업 삭제 실패: {e}")
        flash('완료된 작업 삭제에 실패했습니다.', 'error')
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html', todos=[], current_filter='all', total_count=0, active_count=0, completed_count=0, error="페이지를 찾을 수 없습니다"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html', todos=[], current_filter='all', total_count=0, active_count=0, completed_count=0, error="서버 내부 오류가 발생했습니다"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
