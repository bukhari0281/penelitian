from http.server import BaseHTTPRequestHandler, HTTPServer
from PIL import Image
import io
import json
import urllib.parse
import cgi
import os
from models import Produk
from models import Gambar

class SimpleRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/produk':
            produk = Produk.semua()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([p.__dict__ for p in produk]).encode())
        elif self.path.startswith('/produk/'):
            id_produk = int(self.path.split('/')[-1])
            produk = Produk.cari(id_produk)
            if produk:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(produk.__dict__).encode())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/produk':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = urllib.parse.unquote_plus(post_data.decode('utf-8'))
            data_dict = {}
            for item in post_data.split('&'):
                key, value = item.split('=')
                data_dict[key] = value

            nama_produk = data_dict.get('nama')
            harga_produk = int(data_dict.get('harga'))

            if nama_produk and harga_produk:
                # Gunakan metode tambah() dari model Produk
                id_produk_baru = Produk.tambah(nama_produk, harga_produk)
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'id': id_produk_baru}).encode()) 
            else:
                self.send_response(400)  # Bad Request
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        if self.path.startswith('/produk/'):
            id_produk = int(self.path.split('/')[-1])

            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            put_data = urllib.parse.unquote_plus(put_data.decode('utf-8'))
            data_dict = {}
            for item in put_data.split('&'):
                key, value = item.split('=')
                data_dict[key] = value

            nama_produk_baru = data_dict.get('nama')
            harga_produk_baru = int(data_dict.get('harga'))

            if nama_produk_baru and harga_produk_baru:
                # Gunakan metode ubah() dari model Produk
                jumlah_baris_terpengaruh = Produk.ubah(id_produk, nama_produk_baru, harga_produk_baru)
                if jumlah_baris_terpengaruh > 0:
                    self.send_response(200)  # OK
                else:
                    self.send_response(404)  # Not Found (jika produk tidak ditemukan)
                self.end_headers()
            else:
                self.send_response(400)  # Bad Request
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/produk/'):
            id_produk = int(self.path.split('/')[-1])

            # Gunakan metode hapus() dari model Produk
            jumlah_baris_terpengaruh = Produk.hapus(id_produk)
            if jumlah_baris_terpengaruh > 0:
                self.send_response(204)  # No Content
            else:
                self.send_response(404)  # Not Found (jika produk tidak ditemukan)
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