import http.server
import socketserver
import os
import sys


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')


class RouterHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Map pretty routes to static files
        route_map = {
            '/': 'registration.html',
            '/register': 'registration.html',
            '/login': 'login.html',
            '/student': 'student.html',
            '/teacher': 'teacher.html',
            '/admin': 'admin.html',
        }
        target = route_map.get(path, path.lstrip('/'))
        full = os.path.join(FRONTEND_DIR, target)
        # Fallback to 404 if not exists
        if not os.path.commonpath([FRONTEND_DIR, os.path.abspath(full)]) == FRONTEND_DIR:
            return os.path.join(FRONTEND_DIR, 'login.html')
        return full

    def log_message(self, format, *args):
        try:
            return super().log_message(format, *args)
        except Exception:
            pass


def run(port=5000):
    os.chdir(FRONTEND_DIR)
    with socketserver.TCPServer(('', port), RouterHandler) as httpd:
        print(f"Serving frontend at http://localhost:{port}")
        httpd.serve_forever()


if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    except Exception:
        port = 5000
    run(port)


