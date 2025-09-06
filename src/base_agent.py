# Base agent 

import os
import json
import asyncio
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

#Configuration Models
class AgentConfig(BaseModel):
    agent_id: str
    public_ip: str
    llm_provider: str
    llm_model: str
    framework: str
    capabilities: list = []
    metadata: dict = {}

class TaskRequest(BaseModel):
    task_id: str = "default"
    prompt: str
    context: Optional[Dict] = {}
    priority: int = 1

class TaskResponse(BaseModel):
    task_id: str
    agent_id: str
    result: str
    status: str
    execution_time: float

class BaseAgent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.app = FastAPI(title=f"Agent {config.agent_id}")
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "agent_id": self.config.agent_id,
                "config": self.config.dict()
            }

        @self.app.get("/agentfacts.json")
        async def agent_facts():
            """NANDA-compatible AgentFacts endpoint"""
            return {
                "agent_id": self.config.agent_id,
                "name": f"Agent {self.config.agent_id}",
                "description": f"{self.config.framework} agent using {self.config.llm_model}",
                "version": "1.0.0",
                "endpoints": {
                    "health": f"http://{self.config.public_ip}:8080/health",
                    "task": f"http://{self.config.public_ip}:8080/task",
                    "api_docs": f"http://{self.config.public_ip}:8080/docs"
                },
                "capabilities": self.config.capabilities,
                "protocols": ["HTTP", "REST"],
                "llm_config": {
                    "provider": self.config.llm_provider,
                    "model": self.config.llm_model,
                    "framework": self.config.framework
                },
                "location": {
                    "region": "whatever",
                    "cloud_provider": "aws"
                },
                "metadata": self.config.metadata,
                "status": "active"
            }
        
        @self.app.post("/task", response_model=TaskResponse)
        async def process_task(task: TaskRequest):
            try:
                result = await self.execute_task(task)
                return TaskResponse(
                    task_id=task.task_id,
                    agent_id=self.config.agent_id,
                    result=result,
                    status="completed",
                    execution_time=0.0
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    @abstractmethod
    async def execute_task(self, task:TaskRequest) -> str:
        """Override this method in specific agent implementations"""
        pass
    

    def run(self, port=8080):
        """Start the agent server"""
        uvicorn.run(self.app, host="0.0.0.0", port=port)