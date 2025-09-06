
from base_agent import BaseAgent, AgentConfig
from langchain_agent import LangChainAgent

def create_agent(config: AgentConfig) -> BaseAgent:
    if config.framework == "crewai":
        return ValueError("NO SUPPORT FOR CREWAI YET")
    elif config.framework == "langchain":
        return LangChainAgent(config)
    elif config.framework == "autogen":
        return ValueError("NO SUPPORT FOR AUTOGEN YET")
    else:
        raise ValueError("Invalid Agent Framework")

if __name__ == "__main__":
    # Example: run a LangChain agent
    config = AgentConfig(
        agent_id="agent-1",
        llm_provider="anthropic",     # or "openai", "ollama"
        public_ip="127.0.0.0",
        llm_model="claude-3-5-haiku-latest",   # pick model from provider
        framework="langchain",     # factory will choose LangChainAgent
        capabilities=["chat"]
    )

    # Factory creates a LangChainAgent instance (subclass of BaseAgent)
    agent = create_agent(config)

    # Start FastAPI server for this agent
    agent.run(port=8080)