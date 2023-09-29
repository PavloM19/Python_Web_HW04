from pathlib import Path
import urllib.parse as urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes
import json
import socket
from threading import Thread
from datetime import datetime

BASE_DIR = Path()

class MainHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        self.save_data_to_json(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urlparse.urlparse(self.path)

        match pr_url.path: 
            case '/':
                self.send_html_file('index.html')
            case '/message':
                self.send_html_file('message.html')
            case _:
                file = BASE_DIR.joinpath(pr_url.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html_file('error.html', 404)

    def send_static(self, file):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header('Content-type', mt[0])
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(file, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())


    def save_data_to_json(self, data):
        data_parse = urlparse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        with open(BASE_DIR.joinpath('storage/data.json'), 'r', encoding='utf-8') as fd:
            data_json = json.load(fd)
        
        data_json[str(datetime.now())] = data_dict
        
        with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding='utf-8') as fd:
            json.dump(data_json, fd, ensure_ascii=False, indent=4) # indent=4 - рекомендація ментора - 
'''
Параметр indent=4 указывает, что каждый уровень вложенности в JSON-строке должен быть отделен от предыдущего уровня 4 пробелами. Это делает JSON-данные более читаемыми для человека, хотя увеличивает объем строки.
Если indent не указан или установлен в None (что является значением по умолчанию), JSON-строка будет минимизирована, то есть все пробелы будут удалены, и JSON-данные будут записаны в строку в самом компактном виде.
'''

def server_socket():
    print('--Socket start--')
    host = socket.gethostname()
    port = 5000

    server_socket = socket.socket(socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    server_socket.listen(2)
    conn, address = server_socket.accept()
    print(f'Connection from {address}')
    with conn:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f'received message: {data}')
        


def run(server_class=HTTPServer, handler_class=MainHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        print('--Start--')
        socket = Thread(target=server_socket)
        socket.start()
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
