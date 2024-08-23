package main

import (
	"html/template"
	"log"
	"net/http"
	"penelitian/be_go/config"
	"penelitian/be_go/handler"
)

func main() {
    config.ConnectDB() 

    http.HandleFunc("/", routeIndexGet)
    http.HandleFunc("/files", handler.UploadHandler(config.DB)) 
    http.HandleFunc("/images/", handler.GetImagesHandler(config.DB))
	http.HandleFunc("/items", handler.ItemHandler(config.DB))
    http.HandleFunc("/items/", handler.ItemHandler(config.DB)) 

    log.Println("Server berjalan pada port 9000")
	http.ListenAndServe(":9000", nil)
}

func routeIndexGet(w http.ResponseWriter, r *http.Request) {
    if r.Method != "GET" {
        http.Error(w, "", http.StatusBadRequest)
        return
    }

    var tmpl = template.Must(template.ParseFiles("view.html"))
    var err = tmpl.Execute(w, nil)

    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
    }
}

