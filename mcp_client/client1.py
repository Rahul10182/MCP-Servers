import asyncio
import json

from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI 

load_dotenv()

SERVERS = {
    "math": {
        "transport": "stdio",
        "command": "/Users/rahulsair/opt/homebrew/bin/uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "/Users/rahulsair/Downloads/MCP-Servers/math_server_mcp/main.py"
        ]
    },

    "expense": {
        "transport": "streamable_http",
        "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
    },
}

async def main():
    client = MultiServerMCPClient(SERVERS)

    try:
        tools = await client.get_tools()

        named_tools = {tool.name: tool for tool in tools}

        print("Available tools:", named_tools.keys())

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        )

        llm_with_tools = llm.bind_tools(tools)

        response = await llm_with_tools.ainvoke(
            "What is 15 * 7?"
        )

        print(response)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())