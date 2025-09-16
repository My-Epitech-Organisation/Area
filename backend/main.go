package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	rand.Seed(time.Now().UnixNano())

	r := gin.Default()

	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3000"},
		AllowMethods:     []string{"GET", "POST"},
		AllowHeaders:     []string{"Origin", "Content-Type"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
	}))

	r.POST("/api/trigger", func(c *gin.Context) {
		log.Println("Action déclenchée par le clic du bouton!")
		c.JSON(http.StatusOK, gin.H{
			"message": "Action traitée avec succès",
		})
	})

	r.GET("/api/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "Le serveur est opérationnel",
		})
	})

	r.GET("/api/weather", func(c *gin.Context) {
		city := c.DefaultQuery("city", "Paris")

		log.Printf("Simulation de données météo pour la ville: %s", city)

		temp := 15.0 + float64(rand.Intn(20)) - 5.0
		feelsLike := temp - 1.0 + (rand.Float64() * 2.0)
		humidity := 40 + rand.Intn(50)
		windSpeed := 1.0 + (rand.Float64() * 9.0)

		weatherDescriptions := []string{
			"ciel dégagé", "quelques nuages", "nuageux", "nuages épars",
			"pluie légère", "pluie modérée", "ensoleillé", "brumeux",
			"orageux", "neige légère", "partiellement nuageux",
		}

		weatherIcons := []string{
			"01d", "02d", "03d", "04d", "09d", "10d", "11d", "13d", "50d",
		}

		descriptionIndex := rand.Intn(len(weatherDescriptions))
		iconIndex := rand.Intn(len(weatherIcons))

		description := weatherDescriptions[descriptionIndex]
		icon := weatherIcons[iconIndex]

		c.JSON(http.StatusOK, gin.H{
			"city":        city,
			"temperature": fmt.Sprintf("%.1f", temp),
			"feelsLike":   fmt.Sprintf("%.1f", feelsLike),
			"humidity":    humidity,
			"windSpeed":   fmt.Sprintf("%.1f", windSpeed),
			"description": description,
			"icon":        icon,
		})

		log.Printf("Données météo simulées pour %s: %.1f°C, %s", city, temp, description)
	})

	log.Println("Démarrage du serveur sur http://localhost:8080")
	if err := r.Run(":8080"); err != nil {
		log.Fatal("Erreur lors du démarrage du serveur:", err)
	}
}
