"""
Configuration utilities for AgentMeter SDK
"""

import os
from typing import Optional, Dict, Any, TYPE_CHECKING
from ..models import AgentMeterConfig

if TYPE_CHECKING:
    from ..client import AgentMeterClient


def get_env_config() -> Dict[str, Any]:
    """Get configuration from environment variables"""
    config = {}
    
    # API key is required
    api_key = os.getenv('AGENTMETER_API_KEY')
    if api_key:
        config['api_key'] = api_key
    
    # Optional configurations
    if project_id := os.getenv('AGENTMETER_PROJECT_ID'):
        config['project_id'] = project_id
    
    if agent_id := os.getenv('AGENTMETER_AGENT_ID'):
        config['agent_id'] = agent_id
    
    if user_id := os.getenv('AGENTMETER_USER_ID'):
        config['user_id'] = user_id
    
    if base_url := os.getenv('AGENTMETER_BASE_URL'):
        config['base_url'] = base_url
    
    if timeout := os.getenv('AGENTMETER_TIMEOUT'):
        try:
            config['timeout'] = int(timeout)
        except ValueError:
            pass
    
    return config


def create_client_from_env() -> Optional['AgentMeterClient']:
    """Create an AgentMeter client from environment variables"""
    config = get_env_config()
    
    if 'api_key' not in config:
        return None
    
    # Import here to avoid circular imports
    from ..client import AgentMeterClient
    return AgentMeterClient(**config) 