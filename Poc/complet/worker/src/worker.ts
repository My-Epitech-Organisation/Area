/*
** EPITECH PROJECT, 2025
** Area
** File description:
** worker
*/

import { Worker, Queue } from "bullmq";
import Redis from "ioredis";

const connection = new Redis(process.env.REDIS_URL || "redis://localhost:6379");
const queue = new Queue("jobs", { connection });

new Worker("jobs", async job => {
  console.log(`Processing job: ${job.name}`, job.data);
}, { connection });

// Add test jobs every 15s if TEST_MODE is enabled
if (process.env.TEST_MODE === "true") {
  setInterval(() => {
    queue.add("test", { at: Date.now() });
  }, 15000);
}
