from flask import Flask, send_from_directory, redirect
import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')


@app.route('/')
def root():
    return redirect('/login')


@app.route('/login')
def page_login():
    return send_from_directory(FRONTEND_DIR, 'login.html')


@app.route('/student')
def page_student():
    return send_from_directory(FRONTEND_DIR, 'student.html')


@app.route('/teacher')
def page_teacher():
    return send_from_directory(FRONTEND_DIR, 'teacher.html')


@app.route('/admin')
def page_admin():
    return send_from_directory(FRONTEND_DIR, 'admin.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


