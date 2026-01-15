import asyncio
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables (API Keys)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "gemini-2.0-flash"


async def main():
    # Initialize Gemini Client
    client = genai.Client(api_key=API_KEY)

    # Define local server parameters
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connection to MCP Server Established.")

            # 1. Gather initial context via the unified Master Tool
            print("Gathering morning context...")
            status_res = await session.call_tool("get_morning_status", arguments={"city": "San Francisco"})
            context = status_res.content[0].text

            # 2. Define wrapper functions for Automatic Function Calling
            async def web_search(query: str):
                result = await session.call_tool("web_search", arguments={"query": query})
                return result.content[0].text

            async def create_draft(subject: str, body: str):
                result = await session.call_tool("create_draft", arguments={"subject": subject, "body": body})
                return result.content[0].text

            # 3. Configure Gemini for Autonomous Action
            config = types.GenerateContentConfig(
                tools=[web_search, create_draft],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
            )

            prompt = (
                f"CONTEXT DATA:\n{context}\n\n"
                "INSTRUCTIONS:\n"
                "1. Summarize the unread emails and upcoming calendar events into a concise briefing.\n"
                "2. If a birthday or significant anniversary is noted, use 'web_search' to find gift ideas.\n"
                "3. If gift ideas are found, use 'create_draft' to prepare a message for me to review.\n"
                "4. Deliver the final briefing in a professional tone."
            )

            print("Gemini is analyzing and taking action...")

            # The SDK handles the Call -> Response -> Final Summary loop automatically
            response = await client.aio.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=config
            )

            print(f"\n{'=' * 20} FINAL BRIEFING {'=' * 20}\n")
            print(response.text.strip())
            print(f"\n{'=' * 56}")


if __name__ == "__main__":
    asyncio.run(main())
