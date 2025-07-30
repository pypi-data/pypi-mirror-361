#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "calculator-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Calculator tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "add",
        description: "Add two numbers together",
        inputSchema: {
          type: "object",
          properties: {
            a: { type: "number", description: "First number" },
            b: { type: "number", description: "Second number" },
          },
          required: ["a", "b"],
        },
      },
      {
        name: "subtract",
        description: "Subtract two numbers",
        inputSchema: {
          type: "object",
          properties: {
            a: { type: "number", description: "First number" },
            b: { type: "number", description: "Second number" },
          },
          required: ["a", "b"],
        },
      },
      {
        name: "multiply",
        description: "Multiply two numbers",
        inputSchema: {
          type: "object",
          properties: {
            a: { type: "number", description: "First number" },
            b: { type: "number", description: "Second number" },
          },
          required: ["a", "b"],
        },
      },
      {
        name: "divide",
        description: "Divide two numbers",
        inputSchema: {
          type: "object",
          properties: {
            a: { type: "number", description: "First number (dividend)" },
            b: { type: "number", description: "Second number (divisor)" },
          },
          required: ["a", "b"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (!args || typeof args !== "object") {
    throw new McpError(ErrorCode.InvalidParams, "Invalid arguments");
  }

  switch (name) {
    case "add": {
      const { a, b } = args as { a: number; b: number };
      return {
        content: [
          {
            type: "text",
            text: String(a + b),
          },
        ],
      };
    }

    case "subtract": {
      const { a, b } = args as { a: number; b: number };
      return {
        content: [
          {
            type: "text",
            text: String(a - b),
          },
        ],
      };
    }

    case "multiply": {
      const { a, b } = args as { a: number; b: number };
      return {
        content: [
          {
            type: "text",
            text: String(a * b),
          },
        ],
      };
    }

    case "divide": {
      const { a, b } = args as { a: number; b: number };
      if (b === 0) {
        throw new McpError(ErrorCode.InvalidParams, "Cannot divide by zero");
      }
      return {
        content: [
          {
            type: "text",
            text: String(a / b),
          },
        ],
      };
    }

    default:
      throw new McpError(
        ErrorCode.MethodNotFound,
        `Unknown tool: ${name}`
      );
  }
});

async function runServer() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Calculator MCP server running on stdio");
}

export { server, runServer }; 