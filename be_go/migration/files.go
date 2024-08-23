package migration

import (
	"database/sql"

	_ "github.com/go-sql-driver/mysql" // Ganti dengan driver database yang sesuai
)

func CreateImagesTable(db *sql.DB) { 
    createFilesTable := (`
        CREATE TABLE IF NOT EXISTS files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            path VARCHAR(255) NOT NULL
        )
    `)
    _, err := db.Exec(createFilesTable)
    if err != nil {
        panic(err.Error())
    }
}