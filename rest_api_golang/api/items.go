package api

import (
	"database/sql"
	"log"
	"penelitian/be_go/models"
)

func CreateItem(db *sql.DB, item models.Item) error {
    // Implementasi query INSERT untuk membuat item baru
    insertSQL := "INSERT INTO items (name) VALUES (?)"
    _, err := db.Exec(insertSQL, item.Name)
    return err
}

func GetItems(db *sql.DB) ([]models.Item, error) {
    // Implementasi query SELECT untuk mengambil semua item
    rows, err := db.Query("SELECT id, name FROM items")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var items []models.Item
    for rows.Next() {
        var item models.Item
        if err := rows.Scan(&item.ID, &item.Name); err != nil {
            return nil, err
        }
        items = append(items, item)
    }
    return items, nil
}

func GetItem(db *sql.DB, id int64) (models.Item, error) {
    // Implementasi query SELECT untuk mengambil item berdasarkan ID
    var item models.Item
    err := db.QueryRow("SELECT id, name FROM items WHERE id = ?", id).Scan(&item.ID, &item.Name)
    log.Println("data: ", item.Name)
    return item, err
}

func UpdateItem(db *sql.DB, id int64, item models.Item) error {
    // Implementasi query UPDATE untuk mengubah data item
    updateSQL := "UPDATE items SET name = ? WHERE id = ?"
    _, err := db.Exec(updateSQL, item.Name, id)
    return err
}

func DeleteItem(db *sql.DB, id int64) error {
    // Implementasi query DELETE untuk menghapus item
    deleteSQL := "DELETE FROM items WHERE id = ?"
    _, err := db.Exec(deleteSQL, id)
    return err
}