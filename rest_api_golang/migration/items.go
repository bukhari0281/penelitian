package migration

import (
	"database/sql"

	_ "github.com/go-sql-driver/mysql" // Atau driver database lain yang Anda gunakan
)

func ItemMigrate(db *sql.DB) {
    // Membuat tabel 'items'
    createItemTableSQL := `
    CREATE TABLE IF NOT EXISTS items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );
    `
    _, err := db.Exec(createItemTableSQL)
    if err != nil {
        panic(err.Error())
    }  
}