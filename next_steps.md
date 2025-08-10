### Next steps

- **Model upgrade**: Use Claude 4 for higher-quality answers and more reliable tool calling.

- **Tool calling policy**:
  - Enforce absolute numbers or require the commodity name.
  - Avoid generic questions that obscure intent and may auto-select a commodity.

- **Centralized MCP (FastAPI)**: Create a single FastAPI service to host and expose all tools.

- **Memory architecture**: Store short- and long-term memory in a vector database, partitioned by `thread_id`.

- **Codebase refactor**: Keep only a FastAPI service dedicated to serving CrewAI logic; retire other components.

