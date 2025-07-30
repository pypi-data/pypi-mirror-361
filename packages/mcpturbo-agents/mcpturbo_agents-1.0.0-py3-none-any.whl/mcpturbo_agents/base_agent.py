"""Base agent implementation"""

class BaseAgent:
    """Base class for all MCPTurbo agents"""
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.status = "idle"
        
    async def execute_task(self, task):
        """Execute assigned task"""
        # Implementation will be added
        pass
