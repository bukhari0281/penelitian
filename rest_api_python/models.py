import mysql.connector
import os

# Konfigurasi database
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'db_rest_api_python'

# Koneksi ke database
mydb = mysql.connector.connect(
  host=DB_HOST,
  user=DB_USER,
  password=DB_PASSWORD,
  database=DB_NAME
)

# Membuat cursor
cursor = mydb.cursor()

# Membuat tabel produk jika belum ada
cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        """)

class Item:
    def __init__(self, id=None, nama=None):
        self.id = id
        self.nama = nama

    def semua():
        cursor.execute("SELECT * FROM items")
        hasil = cursor.fetchall()
        item = []
        for row in hasil:
            item.append(Item(row[0], row[1], row[2]))
        return item

    def cari(id):
        cursor.execute("SELECT * FROM items WHERE id = %s", (id,))
        row = cursor.fetchone()
        if row:
            return Item(row[0], row[1], row[2])
        else:
            return None
        
    def tambah(name):
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO items (name) VALUES (%s)", (name,))
        mydb.commit()
        return cursor.lastrowid  # Mengembalikan ID item yang baru ditambahkan

    def ubah(id, nama_baru):
        cursor = mydb.cursor()
        cursor.execute("UPDATE items SET name = %s WHERE id = %s", (nama_baru, id))
        mydb.commit()
        return cursor.rowcount  # Mengembalikan jumlah baris yang terpengaruh (0 atau 1)

    def hapus(id):
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM items WHERE id = %s", (id,))
        mydb.commit()
        return cursor.rowcount  # Mengembalikan jumlah baris yang terpengaruh (0 atau 1)
 

# cursor.execute('''
# CREATE TABLE IF NOT EXISTS gambar (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     filename VARCHAR(255) NOT NULL,
#     path VARCHAR(255) NOT NULL
# )
# ''')

class Gambar:
    def __init__(self, id=None, filename=None, path=None):
        self.id = id
        self.filename = filename
        self.path = path

    def tambah(filename, path):
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO gambar (filename, path) VALUES (%s, %s)", (filename, path))
        mydb.commit()
        return cursor.lastrowid

    def semua():
        cursor.execute("SELECT * FROM gambar")
        hasil = cursor.fetchall()
        gambar = []
        for row in hasil:
            gambar.append(Gambar(row[0], row[1], row[2]))
        return gambar

    def cari(id):
        cursor.execute("SELECT * FROM gambar WHERE id = %s", (id,))
        row = cursor.fetchone()
        if row:
            return Gambar(row[0], row[1], row[2])
        else:
            return None