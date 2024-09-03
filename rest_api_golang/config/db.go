package config

import (
	"database/sql"
	"log"
	"penelitian/be_go/migration"

	_ "github.com/go-sql-driver/mysql"
)

var DB *sql.DB

func ConnectDB() {
	db, err := sql.Open("mysql", "root:@/penelitian")
	if err != nil {
		panic(err)
	}

	log.Println("Connected to database")
	DB = db

	log.Println("Database migrated")
	migration.ItemMigrate(db)
	migration.CreateImagesTable(db)

}