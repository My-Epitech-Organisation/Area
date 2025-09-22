/*
** EPITECH PROJECT, 2025
** Area
** File description:
** index
*/

import Fastify from "fastify";
import { Client } from "pg";
import Redis from "ioredis";
import { Queue } from "bullmq";

const server = Fastify();

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

const redis = new Redis(process.env.REDIS_URL || "redis://localhost:6379");
const queue = new Queue("jobs", { connection: redis });

server.get("/about.json", async (req, reply) => {
  const ip = (req.headers["x-forwarded-for"] || req.socket.remoteAddress) ?? "unknown";
  const now = Math.floor(Date.now() / 1000);

  return {
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
  };
});

server.get("/ping-redis", async () => {
  await redis.set("ping", "pong");
  const pong = await redis.get("ping");
  return { redis: pong };
});

server.get("/test-db", async () => {
  try {
    const result = await db.query("SELECT NOW() as current_time");
    return {
      status: "✅ Database connected",
      timestamp: result.rows[0].current_time,
      message: "PostgreSQL is working correctly!"
    };
  } catch (error) {
    return {
      status: "❌ Database error",
      error: error instanceof Error ? error.message : String(error),
      message: "Failed to connect to PostgreSQL"
    };
  }
});

server.post("/enqueue", async (req, reply) => {
  try {
    const { jobName, data } = req.body as { jobName: string; data: any };

    if (!jobName) {
      return reply.code(400).send({
        status: "❌ Error",
        message: "jobName is required"
      });
    }

    const job = await queue.add(jobName, data || {});
    return {
      status: "✅ Job enqueued",
      jobId: job.id,
      jobName: job.name,
      data: job.data,
      message: `Job "${jobName}" added to queue successfully`
    };
  } catch (error) {
    return reply.code(500).send({
      status: "❌ Error",
      error: error instanceof Error ? error.message : String(error),
      message: "Failed to enqueue job"
    });
  }
});

server.listen(8080, "0.0.0.0", () => {
  console.log("🚀 Server listening on http://0.0.0.0:8080");
});
