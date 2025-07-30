"""
Factory module for creating Policy Manager components.

This module provides utility functions for creating policy manager objects
and their associated components in a consistent manner.
"""
from typing import Optional
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.interfaces.policy_manager.policy_engine import IPolicyEngine
from src.interfaces.policy_manager.policy_config import IPolicyConfig
from src.interfaces.policy_manager.policy_manager import IPolicyManager
from src.policy_manager.policy_engine import PolicyEngine
from src.policy_manager.policy_config import PolicyConfigManager
from src.policy_manager.policy_manager import PolicyManager


class PolicyManagerFactory:
    """Factory class for creating Policy Manager components."""
    
    @staticmethod
    def create_policy_engine(logging_manager: LoggingManager, 
                           config_manager: ConfigManager) -> IPolicyEngine:
        """
        Create a policy engine instance.
        
        Args:
            logging_manager: Centralized logging manager
            config_manager: Centralized configuration manager
            
        Returns:
            IPolicyEngine: Policy engine instance
        """
        return PolicyEngine(logging_manager, config_manager)
    
    @staticmethod
    def create_policy_config(logging_manager: LoggingManager, 
                           config_manager: ConfigManager) -> IPolicyConfig:
        """
        Create a policy configuration manager instance.
        
        Args:
            logging_manager: Centralized logging manager
            config_manager: Centralized configuration manager
            
        Returns:
            IPolicyConfig: Policy configuration manager instance
        """
        return PolicyConfigManager(logging_manager, config_manager)
    
    @staticmethod
    def create_policy_manager(logging_manager: LoggingManager, 
                            config_manager: ConfigManager,
                            policy_engine: Optional[IPolicyEngine] = None,
                            policy_config: Optional[IPolicyConfig] = None) -> IPolicyManager:
        """
        Create a policy manager instance with optional dependency injection.
        
        Args:
            logging_manager: Centralized logging manager
            config_manager: Centralized configuration manager
            policy_engine: Optional policy engine instance (created if None)
            policy_config: Optional policy config instance (created if None)
            
        Returns:
            IPolicyManager: Policy manager instance
        """
        # Create components if not provided
        if policy_engine is None:
            policy_engine = PolicyManagerFactory.create_policy_engine(logging_manager, config_manager)
        
        if policy_config is None:
            policy_config = PolicyManagerFactory.create_policy_config(logging_manager, config_manager)
        
        return PolicyManager(logging_manager, config_manager, policy_engine, policy_config)
    
    @staticmethod
    def create_default_policy_manager(logging_manager: LoggingManager, 
                                    config_manager: ConfigManager) -> IPolicyManager:
        """
        Create a policy manager with default components.
        
        Args:
            logging_manager: Centralized logging manager
            config_manager: Centralized configuration manager
            
        Returns:
            IPolicyManager: Policy manager instance with default components
        """
        return PolicyManagerFactory.create_policy_manager(logging_manager, config_manager) 