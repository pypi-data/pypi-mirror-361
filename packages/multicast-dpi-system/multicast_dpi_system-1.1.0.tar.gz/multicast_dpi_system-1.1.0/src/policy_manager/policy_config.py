"""
Policy Configuration Management

Handles loading, saving, and dynamic updating of policy configurations
from YAML files and runtime API calls.
"""
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.interfaces.policy_manager.policy_config import IPolicyConfig
from src.policy_manager.policy_models import PolicyRule, PolicyCondition, PolicyAction, PolicyPriority

class PolicyConfigManager(IPolicyConfig):
    """
    Manages policy configuration loading, validation, and dynamic updates.
    
    Supports YAML-based configuration files and runtime policy updates
    through API or configuration file changes.
    """
    
    def __init__(self, logging_manager: LoggingManager, config_manager: ConfigManager):
        self.logger = logging_manager.get_logger("policy_config")
        self.json_logger = logging_manager.get_json_logger(self.__class__.__name__)
        self.config_manager = config_manager
        
        # Load policy templates from config
        self.policy_templates = self.config_manager.get_config('policy_templates', {})
        
        self.logger.info("PolicyConfigManager initialized")
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load policy configuration from config manager."""
        try:
            config = {
                'policy_manager': self.config_manager.get_config('policy_manager', {}),
                'enforcement': self.config_manager.get_config('enforcement', {}),
                'policy_templates': self.policy_templates
            }
            
            self.logger.info("Loaded policy configuration from config manager")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default policy configuration."""
        default_config = {
            'policy_manager': {
                'enabled': True,
                'max_policies': 1000,
                'default_action': 'allow',
                'conflict_resolution': 'priority_based',
                'cache_size': 1000,
                'cleanup_interval_minutes': 60
            },
            'enforcement': {
                'real_time': True,
                'batch_size': 100,
                'max_processing_time_ms': 10,
                'enable_statistics': True
            },
            'policy_templates': {
                'security': {
                    'block_malware': {
                        'conditions': [
                            {'field': 'signatures', 'operator': 'contains', 'value': 'malware'}
                        ],
                        'action': 'block',
                        'priority': 'critical'
                    }
                },
                'qos': {
                    'prioritize_voice': {
                        'conditions': [
                            {'field': 'traffic_category', 'operator': 'equals', 'value': 'voice_call'}
                        ],
                        'action': 'prioritize',
                        'action_parameters': {'priority': 0},
                        'priority': 'high'
                    }
                },
                'bandwidth': {
                    'throttle_streaming': {
                        'conditions': [
                            {'field': 'traffic_category', 'operator': 'equals', 'value': 'video_streaming'},
                            {'field': 'bandwidth_class', 'operator': 'equals', 'value': 'high'}
                        ],
                        'action': 'throttle',
                        'action_parameters': {'bandwidth_mbps': 5},
                        'priority': 'medium'
                    }
                }
            }
        }
        
        # Update config manager with default configuration
        self.config_manager.update_config('policy_manager', default_config['policy_manager'])
        self.config_manager.update_config('enforcement', default_config['enforcement'])
        self.config_manager.update_config('policy_templates', default_config['policy_templates'])
        
        return default_config
    
    def save_configuration(self, config: Dict[str, Any]) -> bool:
        """Save configuration to config manager."""
        try:
            self.config_manager.update_config('policy_manager', config.get('policy_manager', {}))
            self.config_manager.update_config('enforcement', config.get('enforcement', {}))
            self.config_manager.update_config('policy_templates', config.get('policy_templates', {}))
            
            self.logger.info("Saved configuration to config manager")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def create_policy_from_template(self, template_category: str, template_name: str, 
                                  custom_parameters: Optional[Dict[str, Any]] = None) -> Optional[PolicyRule]:
        """Create a policy rule from a template."""
        try:
            template = self.policy_templates.get(template_category, {}).get(template_name)
            if not template:
                self.logger.error(f"Template not found: {template_category}.{template_name}")
                return None
            
            # Create policy conditions
            conditions = []
            for cond_data in template.get('conditions', []):
                condition = PolicyCondition(
                    field=cond_data['field'],
                    operator=cond_data['operator'],
                    value=cond_data['value'],
                    case_sensitive=cond_data.get('case_sensitive', False)
                )
                conditions.append(condition)
            
            # Apply custom parameters if provided
            action_parameters = template.get('action_parameters', {}).copy()
            if custom_parameters:
                action_parameters.update(custom_parameters)
            
            # Create policy rule
            policy = PolicyRule(
                name=f"{template_category}_{template_name}",
                description=template.get('description', f"Policy from template {template_name}"),
                conditions=conditions,
                action=PolicyAction(template['action']),
                action_parameters=action_parameters,
                priority=PolicyPriority[template.get('priority', 'medium').upper()]
            )
            
            return policy
            
        except Exception as e:
            self.logger.error(f"Failed to create policy from template: {e}")
            return None
    
    def export_policies_to_file(self, policies: List[PolicyRule], export_path: str) -> bool:
        """Export policies to a file for backup or sharing."""
        try:
            policies_data = []
            for policy in policies:
                policy_dict = {
                    'rule_id': policy.rule_id,
                    'name': policy.name,
                    'description': policy.description,
                    'conditions': [
                        {
                            'field': c.field,
                            'operator': c.operator,
                            'value': c.value,
                            'case_sensitive': c.case_sensitive
                        }
                        for c in policy.conditions
                    ],
                    'action': policy.action.value,
                    'action_parameters': policy.action_parameters,
                    'priority': policy.priority.value,
                    'status': policy.status.value,
                    'created_time': policy.created_time,
                    'expiry_time': policy.expiry_time
                }
                policies_data.append(policy_dict)
            
            with open(export_path, 'w') as f:
                json.dump(policies_data, f, indent=2)
            
            self.logger.info(f"Exported {len(policies)} policies to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export policies: {e}")
            return False
