package database

import (
	"database/sql"
	"errors"
	"log"
)

func GetAllUsers() ([]User, error) {
	rows, err := DB.Query("SELECT id, username, email, role FROM users")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var users []User
	for rows.Next() {
		var user User
		err := rows.Scan(&user.ID, &user.Username, &user.Email, &user.Role)
		if err != nil {
			return nil, err
		}
		users = append(users, user)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return users, nil
}

func GetUserByID(id int) (User, error) {
	var user User
	err := DB.QueryRow("SELECT id, username, email, role FROM users WHERE id = $1", id).
		Scan(&user.ID, &user.Username, &user.Email, &user.Role)
	if err != nil {
		if err == sql.ErrNoRows {
			return User{}, errors.New("user not found")
		}
		return User{}, err
	}
	return user, nil
}

func CreateUser(user User) (int, error) {
	var id int
	err := DB.QueryRow(
		"INSERT INTO users (username, email, role) VALUES ($1, $2, $3) RETURNING id",
		user.Username, user.Email, user.Role,
	).Scan(&id)

	if err != nil {
		log.Printf("Error creating user: %v", err)
		return 0, err
	}

	return id, nil
}

func UpdateUser(user User) error {
	_, err := DB.Exec(
		"UPDATE users SET username = $1, email = $2, role = $3 WHERE id = $4",
		user.Username, user.Email, user.Role, user.ID,
	)
	return err
}

func DeleteUser(id int) error {
	result, err := DB.Exec("DELETE FROM users WHERE id = $1", id)
	if err != nil {
		return err
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rowsAffected == 0 {
		return errors.New("user not found")
	}

	return nil
}
