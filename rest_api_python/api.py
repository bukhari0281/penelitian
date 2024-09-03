from http.server import BaseHTTPRequestHandler, HTTPServer
from PIL import Image
import io
import json
import urllib.parse
import cgi
import os
from models import Item
from models import Gambar

class SimpleRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/items':
            item = Item.semua()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([p.__dict__ for p in item]).encode())
        elif self.path.startswith('/items/'):
            id_item = int(self.path.split('/')[-1])
            item = Item.cari(id_item)
            if item:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(item.__dict__).encode())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/items':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type')

            if content_type.startswith('multipart/form-data'):
                # Tangani multipart/form-data
                fields = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST',
                            'CONTENT_TYPE': self.headers['Content-Type'],
                            })

                nama_item = fields.getfirst("name") 

            elif content_type == 'text/plain':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data_dict = {}
                for item in post_data.decode('utf-8').split('&'):
                    key, value = item.split('=')
                    data_dict[key] = value

                nama_item = data_dict.get('name') 

            elif content_type == 'application/json':
                data_dict = json.loads(post_data.decode('utf-8'))
                nama_item = data_dict.get('name')

            else:
                self.send_response(400) 
                self.end_headers()
                return

            if nama_item:
                id_item_baru = Item.tambah(nama_item)
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'id': id_item_baru}).encode()) 
            else:
                self.send_response(400) 
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        if self.path.startswith('/items/'):
            id_item = int(self.path.split('/')[-1])

            content_type = self.headers.get('Content-Type')

            if content_type.startswith('multipart/form-data'):
                # Tangani multipart/form-data
                fields = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'PUT',
                            'CONTENT_TYPE': self.headers['Content-Type'],
                            })

                nama_item_baru = fields.getfirst("name", "")

                if nama_item_baru:
                    jumlah_baris_terpengaruh = Item.ubah(id_item, nama_item_baru)
                    if jumlah_baris_terpengaruh > 0:
                        self.send_response(200)  # OK
                    else:
                        self.send_response(404)  # Not Found (jika item tidak ditemukan)
                    self.end_headers()
                else:
                    self.send_response(400)  # Bad Request
                    self.end_headers()

            elif content_type == 'text/plain':
                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                put_data = urllib.parse.unquote_plus(put_data.decode('utf-8'))
                data_dict = {}
                for item in put_data.split('&'):
                    key, value = item.split('=')
                    data_dict[key] = value

                nama_item_baru = data_dict.get('name')

                if nama_item_baru:
                    jumlah_baris_terpengaruh = Item.ubah(id_item, nama_item_baru)
                    if jumlah_baris_terpengaruh > 0:
                        self.send_response(200)  # OK
                    else:
                        self.send_response(404)  # Not Found (jika item tidak ditemukan)
                    self.end_headers()
                else:
                    self.send_response(400)  # Bad Request
                    self.end_headers()

            else:
                self.send_response(400)  # Bad Request
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/items/'):
            id_item = int(self.path.split('/')[-1])

            # Gunakan metode hapus() dari model Item
            jumlah_baris_terpengaruh = Item.hapus(id_item)
            if jumlah_baris_terpengaruh > 0:
                self.send_response(204)  # No Content
            else:
                self.send_response(404)  # Not Found (jika item tidak ditemukan)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

class ImageHandler(BaseHTTPRequestHandler):
    def image_POST(self):
        if self.path == '/gambar':
            try:
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                if ctype == 'multipart/form-data':
                    pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                    fields = cgi.parse_multipart(self.rfile, pdict) 

                    file_item = fields.get('gambar')
                    if file_item:
                        filename = file_item[0]['filename']
                        file_data = file_item[0]['body']

                        # Buat folder "gambar" jika belum ada
                        if not os.path.exists('gambar'):
                            os.makedirs('gambar')

                        # Simpan gambar ke folder "gambar"
                        filepath = os.path.join('gambar', filename)
                        with open(filepath, 'wb') as f:
                            f.write(file_data)

                        # Simpan informasi gambar ke database (dengan path)
                        id_gambar_baru = Gambar.tambah(filename, filepath)

                        self.send_response(201)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'id': id_gambar_baru, 'filepath': filepath}).encode())
                    else:
                        self.send_response(400)  # Bad Request
                        self.end_headers()
                else:
                    self.send_response(400)  # Bad Request
                    self.end_headers()
            except Exception as e:
                self.send_response(500)  # Internal Server Error
                self.end_headers()
                print("Error saat memproses unggah gambar:", e)
        else:
            self.send_response(404)
            self.end_headers()

    def image_GET(self):
        
        if self.path == '/gambar':
            gambar = Gambar.semua()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # Hanya mengirim informasi dasar gambar (ID dan nama file)
            self.wfile.write(json.dumps([{'id': g.id, 'nama_file': g.nama_file} for g in gambar]).encode())
        elif self.path.startswith('/gambar/'):
            id_gambar = int(self.path.split('/')[-1])
            gambar = Gambar.cari(id_gambar)
            if gambar:
                filepath = gambar.path  # Ambil path dari database
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        file_data = f.read()
                    self.send_response(200)
                    self.send_header('Content-type', 'image/jpeg')  # Atau sesuaikan dengan tipe gambar Anda
                    self.end_headers()
                    self.wfile.write(file_data)
                else:
                    self.send_response(404)  # Not Found (jika file tidak ditemukan)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()    

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleRequestHandler, ImageHandler)
    print('Server berjalan di port 8000...')
    httpd.serve_forever()