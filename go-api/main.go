package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
	_ "github.com/mattn/go-sqlite3"
)

type Attraction struct {
	ID          int    `json:"id"`
	Title       string `json:"title"`
	Location    string `json:"location"`
	DetailLink  string `json:"detail_link"`
	Page        int    `json:"page"`
	Address     string `json:"address,omitempty"`
	Phone       string `json:"phone,omitempty"`
	Description string `json:"description,omitempty"`
}

var db *sql.DB
var logger *log.Logger

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "../Storage/attractions.db") // Adjust the path as necessary
	if err != nil {
		logger.Fatal("Error connecting to the database: ", err)
	}
	logger.Println("Connected to the SQLite database.")
}

func getAttractions(w http.ResponseWriter, r *http.Request) {
	logger.Println("Received request for attractions")
	w.Header().Set("Content-Type", "application/json")
	var attractions []Attraction

	rows, err := db.Query("SELECT id, title, location, detail_link, page, address, phone, description FROM attractions")
	if err != nil {
		logger.Println("Error querying database: ", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	for rows.Next() {
		var a Attraction
		if err := rows.Scan(&a.ID, &a.Title, &a.Location, &a.DetailLink, &a.Page, &a.Address, &a.Phone, &a.Description); err != nil {
			logger.Println("Error scanning database row: ", err)
			continue
		}
		attractions = append(attractions, a)
	}

	if err := json.NewEncoder(w).Encode(attractions); err != nil {
		logger.Println("Error encoding JSON response: ", err)
	}
}

func main() {
	// Initialize logger
	logger = log.New(os.Stdout, "INFO: ", log.Ldate|log.Ltime|log.Lshortfile)

	initDB()
	defer db.Close()

	r := mux.NewRouter()

	// Custom error handlers
	r.NotFoundHandler = http.HandlerFunc(notFoundHandler)
	r.MethodNotAllowedHandler = http.HandlerFunc(methodNotAllowedHandler)

	// Routes
	r.HandleFunc("/attractions", getAttractions).Methods("GET")

	// rout for robots.txt
	r.HandleFunc("/robots.txt", robotsHandler).Methods("GET")

	// Inside func main()
	r.HandleFunc("/attractions/{id:[0-9]+}", getAttractionByID).Methods("GET")
	r.HandleFunc("/search", searchAttractions).Methods("GET")

	// Register routes for fetching specific columns by ID
	r.HandleFunc("/attractions/{id:[0-9]+}/location", getAttractionDetailByColumn("location")).Methods("GET")
	r.HandleFunc("/attractions/{id:[0-9]+}/address", getAttractionDetailByColumn("address")).Methods("GET")

	// Logging middleware to log all incoming requests
	r.Use(loggingMiddleware)

	fmt.Println("Starting server on :8080")
	log.Fatal(http.ListenAndServe(":8080", r))
}

// notFoundHandler handles requests for routes that do not exist.
func notFoundHandler(w http.ResponseWriter, r *http.Request) {
	logger.Printf("404 Not Found: %s", r.RequestURI)
	http.Error(w, "404 not found", http.StatusNotFound)
}

// methodNotAllowedHandler handles requests with disallowed methods.
func methodNotAllowedHandler(w http.ResponseWriter, r *http.Request) {
	logger.Printf("405 Method Not Allowed: %s", r.RequestURI)
	http.Error(w, "405 method not allowed", http.StatusMethodNotAllowed)
}

// loggingMiddleware logs the details of the request.
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		logger.Printf("Request - Method: %s, URI: %s", r.Method, r.RequestURI)
		next.ServeHTTP(w, r)
	})
}

// robotsHandler handles requests for robots.txt
func robotsHandler(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "robots.txt")
}

func getAttractionByID(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	var a Attraction
	err := db.QueryRow("SELECT id, title, location, detail_link, page, address, phone, description FROM attractions WHERE id = ?", id).Scan(&a.ID, &a.Title, &a.Location, &a.DetailLink, &a.Page, &a.Address, &a.Phone, &a.Description)
	if err != nil {
		if err == sql.ErrNoRows {
			http.NotFound(w, r)
			return
		}
		logger.Println("Error querying database: ", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	if err := json.NewEncoder(w).Encode(a); err != nil {
		logger.Println("Error encoding JSON response: ", err)
	}
}

func searchAttractions(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")
	if query == "" {
		http.Error(w, "Query parameter 'q' is required", http.StatusBadRequest)
		return
	}

	var attractions []Attraction
	rows, err := db.Query("SELECT id, title, location, detail_link, page, address, phone, description FROM attractions WHERE title LIKE ? OR location LIKE ? OR description LIKE ?", "%"+query+"%", "%"+query+"%", "%"+query+"%")
	if err != nil {
		logger.Println("Error querying database: ", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	for rows.Next() {
		var a Attraction
		if err := rows.Scan(&a.ID, &a.Title, &a.Location, &a.DetailLink, &a.Page, &a.Address, &a.Phone, &a.Description); err != nil {
			logger.Println("Error scanning database row: ", err)
			continue
		}
		attractions = append(attractions, a)
	}

	if err := json.NewEncoder(w).Encode(attractions); err != nil {
		logger.Println("Error encoding JSON response: ", err)
	}
}

// Function to create a handler for fetching a specific column value by ID
func getAttractionDetailByColumn(column string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		id := vars["id"]

		// Define a map of allowed column names to prevent SQL injection
		allowedColumns := map[string]bool{
			"location": true,
			"address":  true,
			"phone":    true,
			"title":    true,
			// Add other columns as needed
		}

		// Check if the requested column is allowed
		if _, ok := allowedColumns[column]; !ok {
			logger.Printf("Invalid column name requested: %s", column)
			http.Error(w, "Invalid column name", http.StatusBadRequest)
			return
		}

		// Prepare the SQL query using the validated column name
		query := fmt.Sprintf("SELECT %s FROM attractions WHERE id = ?", column)

		var result string
		err := db.QueryRow(query, id).Scan(&result)
		if err != nil {
			if err == sql.ErrNoRows {
				http.NotFound(w, r)
				return
			}
			logger.Printf("Error querying database for column %s: %v", column, err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		// Encode and send the result
		response := map[string]string{column: result}
		if err := json.NewEncoder(w).Encode(response); err != nil {
			logger.Printf("Error encoding JSON response for column %s: %v", column, err)
		}
	}
}
