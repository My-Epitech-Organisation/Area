/*
** EPITECH PROJECT, 2025
** Area
** File description:
** index
*/

import express, { Request, Response } from "express";
import { Client } from "pg";
import Redis from "ioredis";
import { Queue } from "bullmq";
import { User, CreateUserRequest, UpdateUserRequest } from "./models/User";

const app = express();
const port = 8080;

app.use(express.json());

const db = new Client({
  connectionString: process.env.DATABASE_URL,
});

// Connect to database with retry logic
const connectWithRetry = async (retries = 5, delay = 2000) => {
  for (let i = 0; i < retries; i++) {
    try {
      await db.connect();
      console.log("✅ Connected to PostgreSQL database");
      return;
    } catch (error) {
      console.log(`❌ Database connection attempt ${i + 1}/${retries} failed:`, error instanceof Error ? error.message : String(error));
      if (i < retries - 1) {
        console.log(`⏳ Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  throw new Error("Failed to connect to database after all retries");
};

connectWithRetry().catch(error => {
  console.error("❌ Fatal: Could not connect to database:", error);
  process.exit(1);
});

// Create users table if it doesn't exist
const createUsersTable = async () => {
  try {
    await db.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    console.log("✅ Users table ready");
  } catch (error) {
    console.error("❌ Error creating users table:", error);
  }
};

createUsersTable();

const redis = new Redis(process.env.REDIS_URL || "redis://localhost:6379");
const queue = new Queue("jobs", { connection: redis });

// User CRUD endpoints
app.get("/users", async (req: Request, res: Response) => {
  try {
    const result = await db.query("SELECT * FROM users ORDER BY created_at DESC");
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch users" });
  }
});

app.get("/users/:id", async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const result = await db.query("SELECT * FROM users WHERE id = $1", [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "User not found" });
    }

    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch user" });
  }
});

app.post("/users", async (req: Request, res: Response) => {
  try {
    const { name, email }: CreateUserRequest = req.body;

    if (!name || !email) {
      return res.status(400).json({ error: "Name and email are required" });
    }

    const result = await db.query(
      "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
      [name, email]
    );

    res.status(201).json(result.rows[0]);
  } catch (error: any) {
    if (error.code === '23505') { // Unique constraint violation
      res.status(409).json({ error: "Email already exists" });
    } else {
      res.status(500).json({ error: "Failed to create user" });
    }
  }
});

app.put("/users/:id", async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { name, email }: UpdateUserRequest = req.body;

    if (!name && !email) {
      return res.status(400).json({ error: "At least one field (name or email) is required" });
    }

    const updates = [];
    const values = [];
    let paramCount = 1;

    if (name) {
      updates.push(`name = $${paramCount}`);
      values.push(name);
      paramCount++;
    }

    if (email) {
      updates.push(`email = $${paramCount}`);
      values.push(email);
      paramCount++;
    }

    values.push(id);

    const result = await db.query(
      `UPDATE users SET ${updates.join(', ')} WHERE id = $${paramCount} RETURNING *`,
      values
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "User not found" });
    }

    res.json(result.rows[0]);
  } catch (error: any) {
    if (error.code === '23505') {
      res.status(409).json({ error: "Email already exists" });
    } else {
      res.status(500).json({ error: "Failed to update user" });
    }
  }
});

app.delete("/users/:id", async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const result = await db.query("DELETE FROM users WHERE id = $1 RETURNING *", [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "User not found" });
    }

    res.json({ message: "User deleted successfully" });
  } catch (error) {
    res.status(500).json({ error: "Failed to delete user" });
  }
});

app.get("/about.json", async (req: Request, res: Response) => {
  const ip = (req.headers["x-forwarded-for"] || req.socket.remoteAddress) ?? "unknown";
  const now = Math.floor(Date.now() / 1000);

  res.json({
    client: { host: ip },
    server: {
      current_time: now,
      services: [
        {
          name: "timer",
          actions: [{ name: "time_is", description: "Triggers on specific time" }],
          reactions: [{ name: "notify", description: "Send notification" }]
        }
      ]
    }
  });
});

app.get("/ping-redis", async (req: Request, res: Response) => {
  try {
    await redis.set("ping", "pong");
    const pong = await redis.get("ping");
    res.json({ redis: pong });
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : String(error) });
  }
});

app.get("/test-db", async (req: Request, res: Response) => {
  try {
    const result = await db.query("SELECT NOW() as current_time");
    res.json({
      status: "✅ Database connected",
      timestamp: result.rows[0].current_time,
      message: "PostgreSQL is working correctly!"
    });
  } catch (error) {
    res.status(500).json({
      status: "❌ Database error",
      error: error instanceof Error ? error.message : String(error),
      message: "Failed to connect to PostgreSQL"
    });
  }
});

app.post("/enqueue", async (req: Request, res: Response) => {
  try {
    const { jobName, data } = req.body as { jobName: string; data: any };

    if (!jobName) {
      return res.status(400).json({
        status: "❌ Error",
        message: "jobName is required"
      });
    }

    const job = await queue.add(jobName, data || {});
    res.json({
      status: "✅ Job enqueued",
      jobId: job.id,
      jobName: job.name,
      data: job.data,
      message: `Job "${jobName}" added to queue successfully`
    });
  } catch (error) {
    res.status(500).json({
      status: "❌ Error",
      error: error instanceof Error ? error.message : String(error),
      message: "Failed to enqueue job"
    });
  }
});

app.listen(port, "0.0.0.0", () => {
  console.log(`🚀 Server listening on http://0.0.0.0:${port}`);
});
