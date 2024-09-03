package models

type Image struct {
	ID       int    `json:"id"`
	Filename string `json:"filename"`
	Path     string `json:"path"`
}