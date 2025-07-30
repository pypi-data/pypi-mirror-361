"""
Agent Provider (Manager) and Proxy

This module contains the AgentManager and the _ManagedAgentProxy classes,
which are responsible for managing the lifecycle of agent instances and
transparently handling state persistence.
"""
import logging
from typing import Type, Dict, Any, Optional, AsyncGenerator

from .agent_interface import AgentInterface, StructuredAgentInput, StructuredAgentOutput
from .session_storage import SessionStorageInterface

logger = logging.getLogger(__name__)

class _ManagedAgentProxy(AgentInterface):
    """
    A proxy that wraps a real agent instance. It implements the AgentInterface
    so that it's indistinguishable from a real agent to the server.

    Its primary role is to automatically trigger state persistence after
    an interaction.
    """
    def __init__(self, session_id: str, real_agent: AgentInterface, agent_manager: 'AgentManager'):
        self._session_id = session_id
        self._real_agent = real_agent
        self._agent_manager = agent_manager

    async def get_metadata(self) -> Dict[str, Any]:
        """Passes the call to the real agent."""
        return await self._real_agent.get_metadata()

    async def get_system_prompt(self) -> Optional[str]:
        """Passes the call to the real agent."""
        return await self._real_agent.get_system_prompt()

    async def get_current_model(self, session_id: str) -> Optional[str]:
        """Passes the call to the real agent."""
        return await self._real_agent.get_current_model(session_id)
        
    async def get_state(self) -> Dict[str, Any]:
        """Passes the call to the real agent."""
        return await self._real_agent.get_state()

    async def load_state(self, state: Dict[str, Any]):
        """Passes the call to the real agent."""
        await self._real_agent.load_state(state)

    async def handle_message(self, session_id: str, agent_input: StructuredAgentInput) -> StructuredAgentOutput:
        """
        Handles the message using the real agent and then automatically
        persists the new state.
        """
        # 1. Forward the call to the real agent
        response = await self._real_agent.handle_message(session_id, agent_input)
        
        # 2. Automatically persist the state after the call
        logger.debug(f"Proxy: Auto-saving state for session {self._session_id}")
        await self._agent_manager.save_agent_state(self._session_id, self._real_agent)
        
        return response

    async def handle_message_stream(
        self, session_id: str, agent_input: StructuredAgentInput
    ) -> AsyncGenerator[StructuredAgentOutput, None]:
        """
        Handles the message stream using the real agent and then automatically
        persists the new state at the end of the stream.
        """
        # 1. Forward the call to the real agent's stream
        response_generator = self._real_agent.handle_message_stream(session_id, agent_input)
        
        # 2. Yield all parts from the generator to the caller
        async for response_part in response_generator:
            yield response_part
            
        # 3. After the stream is complete, persist the final state
        logger.debug(f"Proxy: Stream finished. Auto-saving state for session {self._session_id}")
        await self._agent_manager.save_agent_state(self._session_id, self._real_agent)

class AgentManager:
    """
    Manages the lifecycle of agent instances. This is the single entry point
    for the server to get a fully prepared agent.
    """
    def __init__(self, storage: SessionStorageInterface):
        self._storage = storage
        self._active_agents: Dict[str, AgentInterface] = {} # A cache for active agent instances

    async def get_agent(self, session_id: str, agent_class: Type[AgentInterface], user_id: str = "") -> AgentInterface:
        """
        Gets a fully initialized agent instance for a given session, wrapped in a
        state-managing proxy.
        
        Args:
            session_id: The session identifier
            agent_class: The agent class to instantiate
            user_id: The user ID for session lookup (optional for backward compatibility)
        """
        # For simplicity, we create a new agent instance for each request.
        # A more advanced implementation could cache and reuse agent instances.
        
        logger.debug(f"AgentManager: Getting agent for session {session_id}, user {user_id}")
        
        # 1. Create a fresh instance of the agent
        real_agent = agent_class()

        # 2. Load session configuration and apply it to the agent if available
        session_data = await self._storage.load_session(user_id, session_id)
        if session_data and session_data.session_configuration:
            logger.debug(f"AgentManager: Found session configuration for session {session_id}. Applying configuration.")
            # If the agent has a configure_session method, call it
            if hasattr(real_agent, 'configure_session'):
                await real_agent.configure_session(session_data.session_configuration)
            else:
                logger.warning(f"AgentManager: Agent {agent_class.__name__} does not have configure_session method. Configuration not applied.")
        else:
            logger.debug(f"AgentManager: No session configuration found for session {session_id}")

        # 3. Load its state from storage
        agent_state = await self._storage.load_agent_state(session_id)
        if agent_state:
            logger.debug(f"AgentManager: Found existing state for session {session_id}. Loading.")
            await real_agent.load_state(agent_state)
        else:
            logger.debug(f"AgentManager: No state found for session {session_id}. Agent will start fresh.")
            # Ensure agent starts with a default empty state if none is found
            await real_agent.load_state({})

        # 4. Wrap the real agent in the proxy
        proxy = _ManagedAgentProxy(session_id, real_agent, self)
        
        return proxy
        
    async def save_agent_state(self, session_id: str, agent_instance: AgentInterface):
        """
        Saves the agent's current state to the storage backend.
        """
        new_state = await agent_instance.get_state()
        await self._storage.save_agent_state(session_id, new_state)
        logger.debug(f"AgentManager: Persisted state for session {session_id}") 