"""本地文章编辑器。

运行 `python tools/editor.py`，浏览器自动打开 http://127.0.0.1:8765/。
写入 GitHub 用的 token 取自 `gh auth token`，页面上不存任何凭据。
"""

import json
import mimetypes
import subprocess
import threading
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
HOST, PORT = '127.0.0.1', 8765
API = 'https://api.github.com'
SECTIONS = {'learning', 'investing', 'prattling', 'digest'}


def gh_token():
    try:
        token = subprocess.check_output(
            ['gh', 'auth', 'token'], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit('取不到 gh token：先运行 gh auth login')
    if not token:
        raise SystemExit('gh 没有登录：先运行 gh auth login')
    return token


class Handler(BaseHTTPRequestHandler):
    token = gh_token()

    def reply(self, status, body, ctype='application/json; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')   # 本地工具，别吃旧缓存
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = unquote(self.path.split('?')[0])
        if path == '/':
            self.reply(200, (ROOT / 'editor.html').read_bytes(), 'text/html; charset=utf-8')
        elif path.startswith('/api/'):
            self.proxy('GET')
        elif path.startswith('/css/'):
            self.serve_file(ROOT.parent / 'static', path[1:])
        elif path.lstrip('/').split('/')[0] in SECTIONS:
            # 预览里的 /learning/xxx.png 直接读 content/ 下的原图，刚上传的也能显示
            self.serve_file(ROOT.parent / 'content', path[1:])
        else:
            self.send_error(404)

    def serve_file(self, base, rel):
        base = base.resolve()
        file = (base / rel).resolve()
        if base not in file.parents or not file.is_file():
            return self.send_error(404)
        ctype = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
        self.reply(200, file.read_bytes(), ctype)

    def do_PUT(self):
        if self.path.startswith('/api/'):
            self.proxy('PUT')
        else:
            self.send_error(405)

    def proxy(self, method):
        body = None
        if method == 'PUT':
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        req = urllib.request.Request(
            API + self.path[len('/api'):],
            data=body,
            method=method,
            headers={
                'Authorization': 'Bearer ' + self.token,
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
                'Content-Type': 'application/json',
                'User-Agent': 'local-editor',
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                self.reply(res.status, res.read())
        except urllib.error.HTTPError as e:
            self.reply(e.code, e.read())
        except urllib.error.URLError as e:
            self.reply(502, json.dumps({'message': str(e.reason)}).encode())

    def log_message(self, fmt, *args):
        print(self.command, self.path)


if __name__ == '__main__':
    try:
        httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        raise SystemExit(f'端口 {PORT} 被占用，可能编辑器已经在跑')
    url = f'http://{HOST}:{PORT}/'
    threading.Timer(0.5, webbrowser.open, [url]).start()
    print(f'编辑器：{url}   Ctrl+C 退出')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n已退出')
