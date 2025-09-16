package main

import (
	"net/http"
	pocbacknosql "zapierpoc/poc-back-nosql"
	pocbacksql "zapierpoc/poc-back-sql"

	"github.com/gin-gonic/gin"
)

type Workflow struct {
	ID      string   `json:"id"`
	Name    string   `json:"name"`
	Actions []string `json:"actions"`
}

type Action struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

var workflows = []Workflow{}
var actions = []Action{
	{ID: "1", Name: "Send Email"},
	{ID: "2", Name: "Log Message"},
	{ID: "3", Name: "Webhook"},
}

func executeWorkflow(c *gin.Context) {
	id := c.Param("id")
	for _, wf := range workflows {
		if wf.ID == id {
			// Simule l'exécution de chaque action
			result := []string{}
			for _, action := range wf.Actions {
				result = append(result, "Action exécutée: "+action)
			}
			c.JSON(http.StatusOK, gin.H{"result": result})
			return
		}
	}
	c.JSON(http.StatusNotFound, gin.H{"error": "Workflow not found"})
}

func main() {
	r := gin.Default()

	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Origin, Content-Type, Accept")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	r.GET("/workflows", func(c *gin.Context) {
		c.JSON(http.StatusOK, workflows)
	})

	r.POST("/workflows", func(c *gin.Context) {
		var wf Workflow
		if err := c.ShouldBindJSON(&wf); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		workflows = append(workflows, wf)
		c.JSON(http.StatusCreated, wf)
	})

	r.GET("/actions", func(c *gin.Context) {
		c.JSON(http.StatusOK, actions)
	})

	r.POST("/workflows/:id/execute", executeWorkflow)

	pocbacksql.InitSQL()
	pocbacknosql.InitMongo()

	r.POST("/users/sql", pocbacksql.CreateUserSQL)
	r.GET("/users/sql", pocbacksql.GetUsersSQL)
	r.PUT("/users/sql/:id", pocbacksql.UpdateUserSQL)
	r.DELETE("/users/sql/:id", pocbacksql.DeleteUserSQL)
	r.POST("/users/sql/test-add", pocbacksql.AddTestUsersSQL)

	r.POST("/users/nosql", pocbacknosql.CreateUserNoSQL)
	r.GET("/users/nosql", pocbacknosql.GetUsersNoSQL)
	r.PUT("/users/nosql/:id", pocbacknosql.UpdateUserNoSQL)
	r.DELETE("/users/nosql/:id", pocbacknosql.DeleteUserNoSQL)

	r.Run(":8080")
}
