# Taskify: An MCP Server for AI-Driven Code Generation

## Application Scene

Taskify is designed for scenarios where a high-level reasoning or conversational AI needs to delegate complex, multi-step programming tasks to a specialized coding agent. It acts as a structured bridge between understanding a user's request and executing the software development work.

The primary use case is:

1.  An AI Assistant (like a chatbot) receives a high-level request, such as "Build me a simple API for a to-do list."
2.  The Assistant analyzes the request, breaks it down into a logical plan, and formulates a detailed `agent_prompt`.
3.  The Assistant calls the `instruct_coding_agent` tool provided by the Taskify server, passing the prompt.
4.  A dedicated programming agent receives these instructions and performs the actual coding work.

## Value

The core value of Taskify lies in its clear **separation of concerns** and **structured communication protocol**:

*   **Focus:** It allows the high-level AI to focus on understanding, planning, and user interaction, without getting bogged down in the details of code implementation. The programming agent can focus purely on writing and structuring code.
*   **Clarity & Precision:** By formalizing the instruction-passing process via the `agent_prompt`, it reduces ambiguity and ensures the programming agent has a clear, actionable blueprint. This leads to more reliable and accurate execution of tasks.
*   **Extensibility:** Built on the MCP (Multi-purpose Co-pilot Protocol) framework, Taskify can be easily extended with more tools and capabilities in the future, evolving into a more powerful and versatile agentic system.

## Installation and Usage

Taskify is a Python project managed with Poetry.

**Prerequisites:**

*   Python 3.12+
*   Poetry (installation instructions: `pip install poetry`)

**Installation:**

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-repo/taskify.git # Replace with actual repo URL
    cd taskify
    ```
2.  Install dependencies using Poetry:
    ```bash
    poetry install
    ```

**Running the Server:**

The Taskify server can be started using the Poetry run command. This will launch the MCP server, making the `instruct_coding_agent` tool available.

```bash
poetry run taskify
```

Once the server is running, it will expose the `instruct_coding_agent` tool, allowing compatible AI agents to send programming instructions.
