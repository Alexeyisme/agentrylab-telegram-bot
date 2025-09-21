"""
Service registry for centralized service management.
"""

import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Centralized service registry for dependency injection."""
    
    def __init__(self):
        self.adapter: Optional[Any] = None
        self.state_manager: Optional[Any] = None
        self._conversation_service: Optional[Any] = None
        self._preset_service: Optional[Any] = None
    
    def initialize(self, adapter: Any, state_manager: Any) -> None:
        """Initialize services with dependencies."""
        self.adapter = adapter
        self.state_manager = state_manager
        logger.info("Service registry initialized")
    
    def get_conversation_service(self):
        """Get conversation service instance."""
        if not self._conversation_service:
            from .services.conversation_service import ConversationService
            self._conversation_service = ConversationService(self.adapter, self.state_manager)
        return self._conversation_service
    
    def get_preset_service(self):
        """Get preset service instance."""
        if not self._preset_service:
            from .services.preset_service import PresetService
            self._preset_service = PresetService(self.adapter)
        return self._preset_service


# Global service registry
services = ServiceRegistry()
