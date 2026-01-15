# MCP-Personal-Assistant  🤖 Autonomous Morning Briefing Agent
An autonomous Morning Briefing agent built with Gemini 2.0 Flash and the Model Context Protocol (MCP). Features proactive reasoning, multi-turn tool use, and local-first privacy

Gemini 2.0 Flash + Model Context Protocol (MCP)
This repository contains a personal project that implements an autonomous "Executive Assistant" using the Model Context Protocol (MCP). The agent bridges the gap between high-level LLM reasoning and local data silos (Gmail, Calendar, Weather) to provide a proactive morning briefing.

🚀 Project Overview
Most AI assistants are reactive—they wait for a command. This agent is proactive. It doesn't just fetch your schedule; it analyzes it. If it finds a birthday or a gap in your day, it autonomously plans and executes follow-up actions (like researching gift ideas or drafting emails) before you even ask.

The "Golden Run" Milestone
In its final iteration, the agent successfully performed the following workflow:

Parallel Context Gathering: Simultaneously fetched weather, unread emails, and calendar events.

Autonomous Trigger: Identified a birthday for July 2026.

Automatic Function Calling: Independently searched for tech gifts via DuckDuckGo and created a draft in Gmail using the results.

🛠️ Tech Stack & Architecture
LLM: Gemini 2.0 Flash (via Google GenAI SDK)

Protocol: Model Context Protocol (MCP)

Backend: Python 3.13

Integrations: * Google Gmail API: For reading unread mail and creating drafts.

Google Calendar API: For schedule analysis.

DuckDuckGo Search: For real-time web research.

📂 File Structure
server.py: The MCP Capability Provider. This file defines the tools (Gmail, Calendar, Search) and handles the secure OAuth2 connection to Google services.

run_check_mcp.py: The Orchestrator. This script connects to the MCP server and uses Gemini 2.0 to reason through the gathered data and execute tools.

⚙️ Setup & Installation
1. Prerequisites
Google Cloud Project with Gmail and Calendar APIs enabled.

A credentials.json file from the Google Cloud Console.

A Gemini API Key.

2. Environment Setup
Create a .env file in the root directory:

Code snippet

GEMINI_API_KEY=your_api_key_here
3. Installation
Bash

pip install mcp google-genai duckduckgo-search google-auth-oauthlib google-api-python-client python-dotenv
4. Usage
Ensure server.py is in the same directory as run_check_mcp.py:

Bash

python run_check_mcp.py
🧠 Key Learnings
Local-First Privacy: By using MCP, sensitive data like emails and calendar events are processed locally. Only summarized context is sent to the LLM.

Automatic Function Calling: Leveraging the automatic_function_calling configuration in the GenAI SDK removes the need for manual state management in multi-turn conversations.

Asynchronous Performance: Utilizing asyncio.gather for tool execution reduced context-gathering latency by over 50%.

Final Project Status: Feature Complete ✅
The project successfully demonstrates the transition from a simple "Chat-with-Data" bot to a "Reason-and-Act" autonomous agent.
