from base_agent import BaseAgent, AgentConfig, TaskRequest
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

class LangChainAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.llm = self._load_llm()
        self.parser = StrOutputParser()

        # Simple echo-style prompt
        self.prompt = PromptTemplate(
            input_variables=["message"],
            template="You are a helpful assistant. Reply to the following:\n\n{message}"
        )
        self.chain = self.prompt | self.llm | self.parser

    def _load_llm(self):
        """Initialize LLM based on provider"""
        if self.config.llm_provider == "openai":
            return ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=self.config.llm_model
            )
        elif self.config.llm_provider == "anthropic":
            return ChatAnthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model=self.config.llm_model
            )
        elif self.config.llm_provider == "ollama":
            return ChatOllama(model=self.config.llm_model)
        else:
            raise ValueError(f"Unsupported provider: {self.config.llm_provider}")

    async def execute_task(self, task: TaskRequest) -> str:
        """Run the prompt through the LLM"""
        try:
            result = self.chain.invoke({"message": task.prompt})
            return result.strip()
        except Exception as e:
            return f"[Error executing task] {e}"
