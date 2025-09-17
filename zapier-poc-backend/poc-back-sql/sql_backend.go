package pocbacksql

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type User struct {
	ID   uint   `gorm:"primaryKey;autoIncrement" json:"id"`
	Name string `json:"name"`
}

var db *gorm.DB

// Fonction à appeler dans main.go pour initialiser la base
func InitSQL() {
	var err error
	db, err = gorm.Open(sqlite.Open("./users.db"), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	}
	db.AutoMigrate(&User{})
}

// Handler exporté pour créer un utilisateur
func CreateUserSQL(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if err := db.Create(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusCreated, user)
}

// Handler exporté pour lire tous les utilisateurs
func GetUsersSQL(c *gin.Context) {
	var users []User
	if err := db.Find(&users).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, users)
}

func UpdateUserSQL(c *gin.Context) {
	id := c.Param("id")
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if err := db.Model(&User{}).Where("id = ?", id).Update("name", user.Name).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"id": id, "name": user.Name})
}

// Handler pour supprimer un utilisateur
func DeleteUserSQL(c *gin.Context) {
	id := c.Param("id")
	if err := db.Delete(&User{}, "id = ?", id).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"deleted": id})
}

// Handler pour ajouter 100 utilisateurs de test
func AddTestUsersSQL(c *gin.Context) {
	var users []User
	for i := 1; i <= 100; i++ {
		users = append(users, User{
			Name: fmt.Sprintf("User %d", i),
		})
	}
	if err := db.Create(&users).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusCreated, gin.H{"added": 100})
}