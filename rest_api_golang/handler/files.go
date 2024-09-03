package handler

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"penelitian/be_go/models"
	"strings"

	_ "github.com/go-sql-driver/mysql"
)

func UploadHandler(db *sql.DB) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        r.ParseMultipartForm(10 << 20) // max 10 MB
        file, handler, err := r.FormFile("file")
        if err != nil {
            http.Error(w, err.Error(), http.StatusBadRequest)
            return
        }
        defer file.Close()

        filePath := filepath.Join("files", handler.Filename)
        out, err := os.Create(filePath)
        if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        defer out.Close()

        _, err = io.Copy(out, file)
        if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }

        insertImageSQL := `INSERT INTO files (filename, path) VALUES (?, ?)`
        statement, err := db.Prepare(insertImageSQL)
        if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        defer statement.Close()

        _, err = statement.Exec(handler.Filename, filePath)
        if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }

        fmt.Fprintf(w, "File uploaded successfully: %s\n", handler.Filename)
    }
} 

func GetImagesHandler(db *sql.DB) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        if r.Method != "GET" {
            http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
            return
        }

        imageID := strings.TrimPrefix(r.URL.Path, "/images/")

        if imageID == "" {
            // Jika tidak ada ID, tampilkan semua gambar atau data JSON
            rows, err := db.Query("SELECT id, filename, path FROM images") 
            if err != nil {
                http.Error(w, err.Error(), http.StatusInternalServerError)
                return
            }
            defer rows.Close()

            var images []models.Image
            for rows.Next() {
                var img models.Image
                if err := rows.Scan(&img.ID, &img.Filename, &img.Path); err != nil {
                    http.Error(w, err.Error(), http.StatusInternalServerError)
                    return
                }
                images = append(images, img)
            }

            if err := rows.Err(); err != nil {
                http.Error(w, err.Error(), http.StatusInternalServerError)
                return
            }

            // Periksa User-Agent untuk menentukan jenis konten yang akan dikirim
            userAgent := r.Header.Get("User-Agent")
            if strings.Contains(userAgent, "Mozilla") || strings.Contains(userAgent, "Chrome") || strings.Contains(userAgent, "Safari") {
                // Jika dari browser, tampilkan gambar-gambar
                for _, image := range images {
                    displayImage(w, image.Path)
                    fmt.Fprintln(w, "-----") 
                }
            } else {
                // Jika bukan dari browser (misalnya, Postman), kirim data JSON
                w.Header().Set("Content-Type", "application/json")
                json.NewEncoder(w).Encode(images)
            }

        } else {
            // Jika ada ID, tampilkan gambar atau data JSON berdasarkan ID
            var image models.Image
            err := db.QueryRow("SELECT id, filename, path FROM images WHERE id = ?", imageID).Scan(&image.ID, &image.Filename, &image.Path)
            if err != nil {
                if err == sql.ErrNoRows {
                    http.Error(w, "Image not found", http.StatusNotFound)
                } else {
                    http.Error(w, err.Error(), http.StatusInternalServerError)
                }
                return
            }

            userAgent := r.Header.Get("User-Agent")
            if strings.Contains(userAgent, "Mozilla") || strings.Contains(userAgent, "Chrome") || strings.Contains(userAgent, "Safari") {
                displayImage(w, image.Path)
            } else {
                w.Header().Set("Content-Type", "application/json")
                json.NewEncoder(w).Encode(image)
            }
        }
    }
}

func displayImage(w http.ResponseWriter, imagePath string) {
    imgFile, err := os.Open(imagePath)
    if err != nil {
        http.Error(w, "Error opening image: "+imagePath, http.StatusInternalServerError)
        return
    }
    defer imgFile.Close()

    w.Header().Set("Content-Type", http.DetectContentType(make([]byte, 512)))
    _, err = io.Copy(w, imgFile)
    if err != nil {
        http.Error(w, "Error sending image: "+imagePath, http.StatusInternalServerError)
        return
    }
}