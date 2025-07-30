"""
Configuration Generator Factory

Provides factory functions for creating configuration generator instances
with proper dependency injection and configuration.
"""
from typing import Optional
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.interfaces.config_generator import IConfigGenerator
from src.config_generator.config_generator import CiscoConfigGenerator
from src.config_generator.config_manager import ConfigurationManager


def create_config_generator(
    logging_manager: LoggingManager,
    config_manager: ConfigManager,
    generator_type: str = "cisco"
) -> IConfigGenerator:
    """
    Factory function to create a configuration generator instance.
    
    Args:
        logging_manager: Centralized logging manager
        config_manager: Centralized configuration manager
        generator_type: Type of generator to create ("cisco" is currently supported)
        
    Returns:
        IConfigGenerator: Configured configuration generator instance
        
    Raises:
        ValueError: If generator_type is not supported
    """
    if generator_type.lower() == "cisco":
        return CiscoConfigGenerator(logging_manager, config_manager)
    else:
        raise ValueError(f"Unsupported configuration generator type: {generator_type}")


def create_cisco_config_generator(
    logging_manager: LoggingManager,
    config_manager: ConfigManager
) -> CiscoConfigGenerator:
    """
    Factory function to create a Cisco configuration generator instance.
    
    Args:
        logging_manager: Centralized logging manager
        config_manager: Centralized configuration manager
        
    Returns:
        CiscoConfigGenerator: Configured Cisco configuration generator instance
    """
    return CiscoConfigGenerator(logging_manager, config_manager)


def create_configuration_manager(
    logging_manager: LoggingManager,
    config_manager: ConfigManager,
    generator_type: str = "cisco",
    buffer_size: int = 1000,
    generation_interval_packets: int = 1000,
    max_buffer_age_seconds: int = 300
) -> ConfigurationManager:
    """
    Factory function to create a configuration manager instance.
    
    Args:
        logging_manager: Centralized logging manager
        config_manager: Centralized configuration manager
        generator_type: Type of generator to create ("cisco" is currently supported)
        buffer_size: Maximum number of packet contexts to buffer
        generation_interval_packets: Number of packets between configuration generations
        max_buffer_age_seconds: Maximum age of buffer before forcing generation
        
    Returns:
        ConfigurationManager: Configured configuration manager instance
    """
    config_generator = create_config_generator(logging_manager, config_manager, generator_type)
    
    return ConfigurationManager(
        config_generator=config_generator,
        logging_manager=logging_manager,
        config_manager=config_manager,
        buffer_size=buffer_size,
        generation_interval_packets=generation_interval_packets,
        max_buffer_age_seconds=max_buffer_age_seconds
    ) 