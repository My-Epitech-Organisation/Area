package main

import (
	"area/backend/api"
	"area/backend/database"
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"strings"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

type TranslateRequest struct {
	Q      string `json:"q"`
	Source string `json:"source"`
	Target string `json:"target"`
}

type TranslateResponse struct {
	TranslatedText string `json:"translatedText"`
}

func translateWithAPI(text string, sourceLang string, targetLang string) (string, error) {
	apiURL := "https://libretranslate.com/translate"

	log.Printf("Préparation de la requête à l'API de traduction: '%s' de '%s' vers '%s'", text, sourceLang, targetLang)

	data := TranslateRequest{
		Q:      text,
		Source: sourceLang,
		Target: targetLang,
	}

	jsonData, err := json.Marshal(data)
	if err != nil {
		return "", fmt.Errorf("erreur lors de la conversion en JSON: %v", err)
	}

	log.Printf("Envoi de la requête à %s", apiURL)

	req, err := http.NewRequest("POST", apiURL, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("erreur lors de la création de la requête: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("erreur lors de l'envoi de la requête: %v", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("erreur lors de la lecture de la réponse: %v", err)
	}

	log.Printf("Réponse de l'API: Code %d, Corps: %s", resp.StatusCode, string(body))

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("l'API a répondu avec le code %d: %s", resp.StatusCode, body)
	}

	var response TranslateResponse
	if err := json.Unmarshal(body, &response); err != nil {
		return "", fmt.Errorf("erreur lors de l'analyse de la réponse JSON: %v", err)
	}

	return response.TranslatedText, nil
}

func simulateTranslation(text string, targetLang string) (string, error) {
	return "", fmt.Errorf("simulation de traduction désactivée, veuillez utiliser l'API")
}

func main() {
	rand.Seed(time.Now().UnixNano())

	db := database.InitDB()
	defer db.Close()

	err := database.CreateTables(db)
	if err != nil {
		log.Fatalf("Error creating tables: %v", err)
	}

	r := gin.Default()

	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: false,
		MaxAge:           12 * time.Hour,
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

	r.POST("/api/translate", func(c *gin.Context) {
		var request struct {
			Text         string `json:"text"`
			TargetLang   string `json:"targetLang"`
		}

		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Format de requête invalide"})
			return
		}

		if request.Text == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Le texte à traduire est requis"})
			return
		}

		if request.TargetLang == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "La langue cible est requise"})
			return
		}

		log.Printf("Demande de traduction: '%s' vers '%s'", request.Text, request.TargetLang)

		sourceLang := "fr"

		words := strings.Fields(request.Text)
		if len(words) > 1 {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "Pour des raisons de limitation de l'API, veuillez traduire un seul mot à la fois",
				"originalText": request.Text,
				"targetLang": request.TargetLang,
			})
			return
		}

		log.Printf("Tentative de traduction avec l'API LibreTranslate...")
		translatedText, err := translateWithAPI(request.Text, sourceLang, request.TargetLang)
		if err != nil {
			log.Printf("Erreur lors de l'utilisation de l'API: %v.", err)
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "Erreur lors de la connexion à l'API de traduction: " + err.Error(),
				"originalText": request.Text,
				"targetLang": request.TargetLang,
			})
			return
		}

		log.Printf("Traduction via API réussie: '%s'", translatedText)

		c.JSON(http.StatusOK, gin.H{
			"originalText": request.Text,
			"translatedText": translatedText,
			"targetLang": request.TargetLang,
			"sourceLang": sourceLang,
		})

		log.Printf("Traduction effectuée: '%s' -> '%s'", request.Text, translatedText)
	})

	api.RegisterUserRoutes(r)

	log.Println("Démarrage du serveur sur http://localhost:8080")
	if err := r.Run(":8080"); err != nil {
		log.Fatal("Erreur lors du démarrage du serveur:", err)
	}
}
