#!/usr/bin/env node

import { runServer } from "./server.js";

async function main() {
  try {
    await runServer();
  } catch (error) {
    console.error("Server error:", error);
    process.exit(1);
  }
}

// Handle process termination gracefully
process.on("SIGINT", () => {
  console.error("Server shutting down...");
  process.exit(0);
});

process.on("SIGTERM", () => {
  console.error("Server shutting down...");
  process.exit(0);
});

main().catch((error) => {
  console.error("Failed to start server:", error);
  process.exit(1);
}); 