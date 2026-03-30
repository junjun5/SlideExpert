import os
import logging
import vertexai
from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from vertexai.agent_engines.templates.adk import AdkApp

from slide_app.agent import app as adk_app

load_dotenv()

class AgentEngineApp(AdkApp):
    def set_up(self) -> None:
        """Initialize the agent engine app."""
        vertexai.init()
        super().set_up()
        logging.basicConfig(level=logging.INFO)

# Configuration for Agent Engine
PROJECT_ID = "YOUR_PROJECT_ID"
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Minimal wrapper for Reasoning Engine
agent_engine = AgentEngineApp(
    app=adk_app,
    artifact_service_builder=lambda: InMemoryArtifactService(),
)
