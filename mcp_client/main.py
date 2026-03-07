import asyncio
import json

from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI 

load_dotenv()

SERVERS = {
    "math": {
        "transport": "stdio",
        "command": "uv",
        "args": [
            "--directory",
            "/Users/rahulsair/Downloads/MCP-Servers/math_server_mcp",
            "run",
            "python",
            "main.py"
        ]
    },

    "expense": {
        "transport": "streamable_http",
        "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
    }
}

async def main():
    client = MultiServerMCPClient(SERVERS)
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


if __name__ == "__main__":
    asyncio.run(main())