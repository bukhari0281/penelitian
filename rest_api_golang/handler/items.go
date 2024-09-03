package handler

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"penelitian/be_go/api"
	"penelitian/be_go/models"
	"strconv"
)

func ItemHandler(db *sql.DB) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")

        switch r.Method {
        case "GET":
            if id, err := strconv.ParseInt(r.URL.Path[len("/items/"):], 10, 64); err == nil {
                item, err := api.GetItem(db, id)
                if err != nil {
                    http.Error(w, err.Error(), http.StatusInternalServerError)
                    return
                }
                json.NewEncoder(w).Encode(map[string]string{"message": "Item berhasil diambil", "id": strconv.Itoa(int(item.ID)), "data": item.Name})
            } else {
                items, err := api.GetItems(db)
                if err != nil {
                    http.Error(w, err.Error(), http.StatusInternalServerError)
                    return
                }
                json.NewEncoder(w).Encode(map[string]interface{}{"message": "Daftar item berhasil diambil", "data": items})
            }
        case "POST":
            var item models.Item
            if err := json.NewDecoder(r.Body).Decode(&item); err != nil {
                http.Error(w, err.Error(), http.StatusBadRequest)
                return
            }
            if err := api.CreateItem(db, item); err != nil {
                http.Error(w, err.Error(), http.StatusInternalServerError)
                return
            }
            w.WriteHeader(http.StatusCreated)
            json.NewEncoder(w).Encode(map[string]string{"message":"Item berhasil dibuat"})
        case "PUT":
            if id, err := strconv.ParseInt(r.URL.Path[len("/items/"):], 10, 64); err == nil {
                var item models.Item
                if err := json.NewDecoder(r.Body).Decode(&item); err != nil {
                    http.Error(w, err.Error(), http.StatusBadRequest)
                    return
                }
                if err := api.UpdateItem(db, id, item); err != nil {
                    http.Error(w, "Gagal mengubah item", http.StatusInternalServerError)
                    return
                } 
                json.NewEncoder(w).Encode(map[string]string{"message": "Item berhasil diubah"})
            } else {
                http.Error(w, "ID tidak valid", http.StatusBadRequest)
            }
        case "DELETE":
            if id, err := strconv.ParseInt(r.URL.Path[len("/items/"):], 10, 64); err == nil {
                if err := api.DeleteItem(db, id); err != nil {
                    http.Error(w, "Gagal menghapus item", http.StatusInternalServerError)
                    return
                }
                json.NewEncoder(w).Encode(map[string]string{"message": "Item berhasil dihapus"})
            } else {
                http.Error(w, "ID tidak valid", http.StatusBadRequest)
            }
        default:
            http.Error(w, "Method tidak diizinkan", http.StatusMethodNotAllowed)
        }
    }
}