package database

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/lib/pq"
)

type User struct {
	ID       int    `json:"id"`
	Username string `json:"username"`
	Email    string `json:"email"`
	Role     string `json:"role"`
}

var DB *sql.DB

func InitDB() *sql.DB {
	host := os.Getenv("DB_HOST")
	if host == "" {
		host = "localhost"
	}
	port := os.Getenv("DB_PORT")
	if port == "" {
		port = "5432"
	}
	user := os.Getenv("DB_USER")
	if user == "" {
		user = "postgres"
	}
	password := os.Getenv("DB_PASSWORD")
	if password == "" {
		password = "postgres"
	}
	dbname := os.Getenv("DB_NAME")
	if dbname == "" {
		dbname = "area_db"
	}

	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatalf("Error connecting to the database: %v", err)
	}

	err = db.Ping()
	if err != nil {
		log.Fatalf("Error pinging the database: %v", err)
	}

	log.Println("Successfully connected to the database")
	DB = db
	return db
}

func CreateTables(db *sql.DB) error {
	createUsersTable := `
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'user'
    );`

	_, err := db.Exec(createUsersTable)
	if err != nil {
		return fmt.Errorf("error creating users table: %v", err)
	}

	var count int
	err = db.QueryRow("SELECT COUNT(*) FROM users").Scan(&count)
	if err != nil {
		return fmt.Errorf("error checking users table: %v", err)
	}

	if count == 0 {
		sampleUsers := []User{
			{Username: "admin", Email: "admin@example.com", Role: "admin"},
			{Username: "user1", Email: "user1@example.com", Role: "user"},
			{Username: "user2", Email: "user2@example.com", Role: "user"},
		}

		for _, user := range sampleUsers {
			_, err := db.Exec(
				"INSERT INTO users (username, email, role) VALUES ($1, $2, $3)",
				user.Username, user.Email, user.Role,
			)
			if err != nil {
				return fmt.Errorf("error inserting sample user: %v", err)
			}
		}
		log.Println("Inserted sample users into the database")
	}

	return nil
}
