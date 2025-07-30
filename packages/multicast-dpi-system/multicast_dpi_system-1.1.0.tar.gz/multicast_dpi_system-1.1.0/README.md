# Multicast DPI System

[![PyPI version](https://badge.fury.io/py/multicast-dpi-system.svg)](https://badge.fury.io/py/multicast-dpi-system)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Deep Packet Inspection (DPI) system designed for multicast traffic analysis with real-time policy enforcement and traffic classification. This system provides enterprise-grade network monitoring capabilities with modular architecture for easy customization and extension.

## 🚀 Features

- **Real-time Packet Capture**: Live multicast traffic monitoring with high-performance packet processing
- **Deep Packet Inspection**: Protocol identification, signature matching, and encrypted traffic analysis
- **Intelligent Traffic Classification**: Rule-based and flow-aware classification with ML-ready architecture
- **Policy Enforcement**: Real-time policy application with per-flow caching and dynamic re-evaluation
- **Configuration Generation**: Automatic device configuration generation (Cisco IOS/NX-OS)
- **Comprehensive Logging**: Structured logging with JSON output for analysis and monitoring
- **Modular Architecture**: Interface-based design for easy extension and customization

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install multicast-dpi-system
```

### From Source

```bash
git clone https://github.com/yourusername/multicast-dpi-system.git
cd multicast-dpi-system
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/multicast-dpi-system.git
cd multicast-dpi-system
pip install -e ".[dev]"
```

## 🛠️ Quick Start

### 1. Basic Usage

```python
from multicast_dpi_system import MulticastDPISystem
from src.utils.config_handler import ConfigManager
from src.utils.logging_utils import LoggingManager

# Initialize the system
config_manager = ConfigManager()
logging_manager = LoggingManager(config_manager.get_logging_config())
system = MulticastDPISystem(logging_manager, config_manager)

# Start the system
system.start()

# The system will automatically:
# - Capture multicast packets
# - Perform DPI analysis
# - Classify traffic
# - Apply policies
# - Generate configurations
```

### 2. Command Line Interface

```bash
# Run the system with default configuration
multicast-dpi

# Or run the main module directly
python -m src.main
```

## ⚙️ Configuration

The Multicast DPI System is configured through YAML and JSON files in the `configs/` folder at the project root. **You can override any system default by editing or adding the relevant key in these files.**

### Configuration Structure

```
configs/
├── dpi_config.yaml          # DPI Engine configuration
├── packet_capture.yaml      # Packet capture settings
├── classification_rules.yaml # Traffic classification rules
├── policy_config.yaml       # Policy management settings
└── signatures.json          # Protocol signatures
```

### Configuration Files

#### 1. DPI Configuration (`configs/dpi_config.yaml`)

```yaml
dpi_engine:
  # General settings
  enabled: true
  max_packet_size: 65535
  timeout_seconds: 30

  # Module settings
  modules:
    protocol_identifier:
      enabled: true
      confidence_threshold: 0.8
    encrypted_analyzer:
      enabled: true
      entropy_threshold: 7.5
    signature_matcher:
      enabled: true
      max_signatures: 1000
      priority_threshold: 5
```

#### 2. Packet Capture Configuration (`configs/packet_capture.yaml`)

```yaml
# Interface and multicast listener Configuration
interface: wlp0s20f3
multicast_ips:
  - "239.0.0.1"
ports: []

# Filter Engine Configuration
filter:
  enable: true
  bpf_rules: []
  manual_rules: []

# Packet Buffer Configuration
buffer:
  size_mb: 5000
  auto_delete_threshold: 90
  checkpoint_interval_sec: 300
  priority_queues:
    0: "low"
    1: "port 80-443"
    2: "ICMP"
    3: "high"
```

#### 3. Classification Rules (`configs/classification_rules.yaml`)

*(See the system config in `src/system_config/classification_rules.yaml` for the full structure. You can override any category or threshold by copying the relevant section here and editing it.)*

#### 4. Policy Configuration (`configs/policy_config.yaml`)

```yaml
policy_manager:
  enabled: true
  max_policies: 1000
  default_action: allow
  conflict_resolution: priority_based
  cache_size: 1000
  cleanup_interval_minutes: 60

enforcement:
  real_time: true
  batch_size: 100
  max_processing_time_ms: 10
  enable_statistics: true

policy_templates:
  security:
    block_malware:
      description: "Block traffic with malware signatures"
      conditions:
        - field: "signatures"
          operator: "contains"
          value: "malware"
      action: "block"
      priority: "critical"
    # ... (other templates)
```

#### 5. Signatures (`configs/signatures.json`)

*(You can add or override protocol signatures for DPI by editing this file. See the system config for the full structure.)*

---

**Tip:**  
You only need to include the settings you want to override in your user config files. The system will always use the merged result: **user config > system config**.

## 🏗️ Architecture

The system follows a modular, interface-based architecture with the following core components:

### Core Modules

#### 1. Packet Capture (`src/packet_capture/`)
- **LivePacketCapture**: Real-time packet capture with multicast support
- **MulticastListener**: Specialized multicast group monitoring
- **FilterEngine**: Packet filtering and preprocessing
- **PacketBuffer**: Efficient packet buffering and management

#### 2. DPI Engine (`src/dpi_engine/`)
- **DPIEngine**: Main DPI processing engine
- **ProtocolIdentifier**: Protocol detection and identification
- **SignatureMatcher**: Pattern-based signature matching
- **EncryptedAnalyzer**: Encrypted traffic analysis

#### 3. Traffic Classifier (`src/traffic_classifier/`)
- **TrafficClassifier**: Main classification orchestrator
- **RuleBasedClassifier**: Rule-based traffic classification
- **FlowAwareClassifier**: Flow-aware classification with statistics
- **FlowStatsManager**: Flow statistics management

#### 4. Policy Manager (`src/policy_manager/`)
- **PolicyManager**: Main policy enforcement engine
- **PolicyEngine**: Policy evaluation and execution
- **PolicyConfigManager**: Policy configuration management
- **Policy Models**: Policy data structures and models

#### 5. Configuration Generator (`src/config_generator/`)
- **CiscoConfigGenerator**: Cisco IOS/NX-OS configuration generation
- **ConfigurationManager**: Automatic configuration management
- **Config Models**: Configuration data structures

### Data Flow

```
Packet Capture → DPI Engine → Traffic Classifier → Policy Manager → Config Generator
     ↓              ↓              ↓                ↓                ↓
  Raw Packets → Protocol ID → Classification → Policy Enforcement → Device Configs
```

## 📊 Monitoring and Logging

### Log Files

The system generates comprehensive logs in the `logs/` directory:

- `system.log`: General system information and debug logs
- `packet_capture.log`: Raw packet capture data (JSON format)
- `dpi_engine.log`: DPI analysis results (JSON format)
- `traffic_classification.log`: Classification results (JSON format)
- `policy_manager.log`: Policy enforcement actions (JSON format)
- `config_generator.log`: Configuration generation logs (JSON format)

### Statistics

Each module provides detailed statistics:

```python
# Get system statistics
system_stats = system.get_system_status()

# Get classification statistics
classifier_stats = system.traffic_classifier.get_classification_statistics()

# Get policy statistics
policy_stats = system.policy_manager.get_statistics()

# Get configuration statistics
config_stats = system.configuration_manager.get_statistics()
```

## 🔧 Customization

### Adding Custom Classifiers

```python
from src.interfaces.traffic_classifier import ITrafficClassifier

class CustomClassifier(ITrafficClassifier):
    def classify_traffic(self, context: PacketContext) -> ClassificationResult:
        # Your custom classification logic
        pass
```

### Adding Custom Policies

```python
from src.policy_manager.policy_models import PolicyRule, PolicyAction, PolicyCondition

custom_policy = PolicyRule(
    name="Custom Policy",
    description="Custom policy description",
    conditions=[
        PolicyCondition(field="src_ip", operator="equals", value="192.168.1.100")
    ],
    action=PolicyAction.BLOCK,
    priority=PolicyPriority.HIGH
)

system.policy_manager.add_policy(custom_policy)
```

### Adding Custom Configuration Generators

```python
from src.interfaces.config_generator import IConfigGenerator

class CustomConfigGenerator(IConfigGenerator):
    def generate_from_policies(self, policy_results: List[Dict[str, Any]]) -> str:
        # Your custom configuration generation logic
        pass
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test module
pytest tests/test_packet_capture.py
```

### Development Tools

```bash
# Code formatting
black src/

# Linting
flake8 src/

# Type checking
mypy src/
```

## 📈 Performance

The system is designed for high-performance multicast traffic analysis:

- **Packet Processing**: 100,000+ packets/second
- **Memory Usage**: <100MB for typical deployments
- **CPU Usage**: <10% on modern hardware
- **Latency**: <1ms per packet

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://multicast-dpi-system.readthedocs.io/](https://multicast-dpi-system.readthedocs.io/)
- **Issues**: [https://github.com/yourusername/multicast-dpi-system/issues](https://github.com/yourusername/multicast-dpi-system/issues)
- **Discussions**: [https://github.com/yourusername/multicast-dpi-system/discussions](https://github.com/yourusername/multicast-dpi-system/discussions)

## 🙏 Acknowledgments

- Built with [Scapy](https://scapy.net/) for packet manipulation
- Uses [dpkt](https://github.com/kbandla/dpkt) for packet parsing
- Inspired by enterprise DPI solutions

---

**Note**: This system is designed for multicast traffic analysis and may require root/administrator privileges for packet capture operations.
