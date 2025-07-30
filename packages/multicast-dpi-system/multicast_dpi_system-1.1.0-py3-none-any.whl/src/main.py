"""
Main Application Entry Point - Multicast DPI System

This module demonstrates industry-level integration of multiple modules:
- Interface-based architecture
- Dependency injection
- Configuration management
- Error handling and logging
- Graceful shutdown
- Module lifecycle management
"""
import sys
import signal
import time
from typing import Optional, Dict, Any

# Core imports
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager

# Concrete implementations
from src.packet_capture.capture_system import LivePacketCapture
from src.dpi_engine.dpi_engine import create_dpi_engine
from src.traffic_classifier.traffic_classifier import create_traffic_classifier
from src.policy_manager.factory import PolicyManagerFactory
from src.config_generator.factory import create_configuration_manager


class MulticastDPISystem:
    """
    Main system orchestrator for the Multicast DPI System.
    Handles module integration, dependency injection, configuration, error handling, and graceful shutdown.
    """
    def __init__(self, logging_manager: LoggingManager, config_manager: ConfigManager):
        self.logging_manager = logging_manager
        self.config_manager = config_manager
        self.logger = self.logging_manager.get_logger('system')
        self.running = False
        self.packet_capture: Optional[LivePacketCapture] = None
        self.dpi_engine = None
        self.traffic_classifier = None
        self.policy_manager = None
        self.configuration_manager = None
        self.stats = {
            'packets_processed': 0,
            'start_time': 0,
            'errors': 0,
            'last_error': None
        }
        self.logger.info("Multicast DPI System initialized")

    def initialize_modules(self) -> bool:
        try:
            self.logger.info("Initializing modules...")
            config_dir = self.config_manager.user_config_dir
            # Packet Capture
            self.packet_capture = LivePacketCapture(
                config_file=str(config_dir / "packet_capture.yaml"),
                logging_manager=self.logging_manager,
                config_manager=self.config_manager
            )
            # DPI Engine
            signatures_file = str(config_dir / "signatures.json")
            self.dpi_engine = create_dpi_engine(
                self.logging_manager,
                self.config_manager,
                signatures_file
            )
            # Traffic Classifier
            import os
            user_rules_file = str(config_dir / "classification_rules.yaml")
            system_rules_file = str(self.config_manager.system_config_dir / "classification_rules.yaml")
            if os.path.isfile(user_rules_file):
                classification_rules_file = user_rules_file
            else:
                classification_rules_file = system_rules_file
            self.traffic_classifier = create_traffic_classifier(
                self.logging_manager, 
                self.config_manager, 
                classification_rules_file
            )
            # Policy Manager
            self.policy_manager = PolicyManagerFactory.create_default_policy_manager(
                self.logging_manager, self.config_manager
            )
            # Configuration Manager
            self.configuration_manager = create_configuration_manager(
                self.logging_manager, self.config_manager
            )
            self.logger.info("All modules initialized successfully")
            return True         
        except Exception as e:
            self.logger.error(f"Failed to initialize modules: {e}", exc_info=True)
            self.stats['last_error'] = str(e)
            return False

    def start(self) -> bool:
        try:
            self.logger.info("Starting Multicast DPI System...")
            if not self.initialize_modules():
                return False
            # Start policy manager
            self.policy_manager.start()
            if not self.packet_capture.start(self._process_packet):
                self.logger.error("Failed to start packet capture")
                return False
            self.stats['start_time'] = time.time()
            self.running = True
            self.logger.info("Multicast DPI System started successfully")
            print(f"✅ Multicast DPI System started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}", exc_info=True)
            self.stats['last_error'] = str(e)
            return False

    def _process_packet(self, context) -> None:
        try:
            self.dpi_engine.analyze_packet(context)
            self.traffic_classifier.classify_traffic(context)
            # Policy Manager integration: apply policies after classification
            self.policy_manager.process_packet(context)
            
            # Configuration Manager: process packet context for automatic configuration generation
            if self.configuration_manager:
                self.configuration_manager.process_packet_context(context)
                
            self.stats['packets_processed'] += 1
            if self.stats['packets_processed'] % 100 == 0:
                self._log_periodic_stats()
        except Exception as e:
            self.logger.error(f"Error processing packet: {e}", exc_info=True)
            self.stats['errors'] += 1
            self.stats['last_error'] = str(e)

    def show_configuration_info(self) -> None:
        """Display information about generated configurations."""
        if not self.configuration_manager:
            print("❌ Configuration manager not initialized")
            return
        
        try:
            self.configuration_manager.show_configuration_info()
        except Exception as e:
            print(f"❌ Error getting configuration info: {e}")

    def _log_periodic_stats(self) -> None:
        try:
            elapsed_time = time.time() - self.stats['start_time']
            packets_per_second = (self.stats['packets_processed'] / elapsed_time if elapsed_time > 0 else 0)
            
            stats_string = (
                f"Rate: {packets_per_second:.1f} pps | "
                f"Errors: {self.stats['errors']}"
            )
            print(f" | {stats_string}", end='\n')
        except Exception as e:
            self.logger.debug(f"Error logging periodic stats: {e}")

    def stop(self) -> None:
        try:
            self.logger.info("Stopping Multicast DPI System...")
            print(f"🛑 Stopping Multicast DPI System...")
            self.running = False
            if self.packet_capture:
                self.packet_capture.stop()
            if self.dpi_engine:
                self.dpi_engine.shutdown()
            if self.traffic_classifier:
                self.traffic_classifier.shutdown()
            if self.policy_manager:
                self.policy_manager.shutdown()
            if self.configuration_manager:
                self.configuration_manager.shutdown()
            self._log_final_stats()
            self.logger.info("Multicast DPI System stopped successfully")
            print(f"✅ Multicast DPI System stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping system: {e}", exc_info=True)
            print(f"❌ Error stopping system: {e}")

    def _log_final_stats(self) -> None:
        try:
            elapsed_time = time.time() - self.stats['start_time']
            packets_per_second = (self.stats['packets_processed'] / elapsed_time if elapsed_time > 0 else 0)
            self.logger.info(
                f"Final Stats: {self.stats['packets_processed']} packets in {elapsed_time:.1f}s "
                f"({packets_per_second:.1f} packets/sec, {self.stats['errors']} errors)"
            )
            print(f"\n📊 Final Statistics:")
            print(f"   - Packets processed: {self.stats['packets_processed']}")
            print(f"   - Processing time: {elapsed_time:.1f}s")
            print(f"   - Processing rate: {packets_per_second:.1f} packets/sec")
            print(f"   - Errors encountered: {self.stats['errors']}")
            if self.stats['last_error']:
                print(f"   - Last error: {self.stats['last_error']}")
            
            # Log configuration generator stats if available
            if self.configuration_manager:
                config_stats = self.configuration_manager.get_statistics()
                manager_stats = config_stats.get('manager', {})
                generator_stats = config_stats.get('generator', {})
                print(f"   - Configurations generated: {manager_stats.get('configurations_generated', 0)}")
                print(f"   - Cisco rules created: {generator_stats.get('cisco_rules_created', 0)}")
                
        except Exception as e:
            self.logger.debug(f"Error logging final stats: {e}")

    def get_configuration_generator_status(self) -> Dict[str, Any]:
        """Get configuration generator status and statistics."""
        if not self.configuration_manager:
            return {'status': 'not_initialized'}
        
        try:
            stats = self.configuration_manager.get_statistics()
            return {
                'status': 'active',
                'supported_vendors': self.configuration_manager.get_supported_vendors(),
                'configuration_format': self.configuration_manager.get_configuration_format(),
                'statistics': stats
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def get_system_status(self) -> Dict[str, Any]:
        return {
            'running': self.running,
            'stats': self.stats.copy(),
            'modules': {
                'packet_capture': self.packet_capture is not None,
                'dpi_engine': self.dpi_engine is not None,
                'traffic_classifier': self.traffic_classifier is not None,
                'policy_manager': self.policy_manager is not None,
                'configuration_manager': self.configuration_manager is not None
            }
        }


class SystemManager:
    """
    High-level system manager for lifecycle management.
    Handles system startup, shutdown, and monitoring.
    """
    def __init__(self):
        self.config_manager = ConfigManager()
        log_config = self.config_manager.get_logging_config()
        self.logging_manager = LoggingManager(log_config)
        self.system: Optional[MulticastDPISystem] = None
        self.logger = self.logging_manager.get_logger('system')

    def start_system(self) -> bool:
        try:
            self.system = MulticastDPISystem(self.logging_manager, self.config_manager)
            return self.system.start()
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}", exc_info=True)
            return False

    def stop_system(self) -> None:
        if self.system:
            self.system.stop()

    def get_status(self) -> Dict[str, Any]:
        if self.system:
            return self.system.get_system_status()
        return {'running': False, 'error': 'System not initialized'}


def signal_handler(signum, frame):
    print(f"\n🛑 Received signal {signum}, shutting down...")
    if hasattr(signal_handler, 'manager'):
        signal_handler.manager.stop_system()
    sys.exit(0)


def main():
    print(f"🚀 Multicast DPI System\n")
    manager = SystemManager()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal_handler.manager = manager
    try:
        if not manager.start_system():
            print(f"❌ Failed to start system")
            sys.exit(1)
        while True:
            time.sleep(3)
            if manager.system and manager.system.running:
                manager.system._log_periodic_stats()
    except KeyboardInterrupt:
        print(f"\n Keyboard interrupt received")
    except Exception as e:
        print(f"❌ System error: {e}")
        manager.logger.error(f"System error: {e}", exc_info=True)

if __name__ == "__main__":
    main() 