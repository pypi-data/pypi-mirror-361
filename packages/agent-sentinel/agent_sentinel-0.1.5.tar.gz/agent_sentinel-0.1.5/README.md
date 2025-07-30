# 🛡️ Agent Sentinel

**Enterprise-grade security monitoring SDK for AI agents**

> **Note:** For Python imports, use `agent_sentinel` (underscore). For installation, CLI, and Docker, use `agent-sentinel` (hyphen).

[![PyPI version](https://badge.fury.io/py/agent-sentinel.svg)](https://badge.fury.io/py/agent-sentinel)
[![Python versions](https://img.shields.io/pypi/pyversions/agent-sentinel.svg)](https://pypi.org/project/agent-sentinel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/sentinel/sentinel/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/sentinel/sentinel/actions)
[![Security](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Agent Sentinel provides comprehensive security monitoring, threat detection, and performance analytics for AI agents in production environments. Built with enterprise-grade features including real-time monitoring, advanced threat detection, and seamless integration capabilities.

---

**📝 Naming Convention:**
- **Project/Brand Name:** Agent Sentinel
- **Python Package, CLI, and Imports:** `agent-sentinel`

---

## ✨ Features

### 🔒 **Security Monitoring**
- **Real-time threat detection** for SQL injection, XSS, command injection, and more
- **Prompt injection protection** with advanced pattern recognition
- **Rate limiting** and abuse prevention
- **Data exfiltration detection** and prevention
- **Encrypted communication** with end-to-end security

### 📊 **Performance Analytics**
- **Method call tracking** and performance metrics
- **Session monitoring** and user behavior analysis
- **Resource usage tracking** and optimization insights
- **Real-time monitoring** with comprehensive logging

### 🏢 **Enterprise Features**
- **Modular architecture** with pluggable components
- **Comprehensive logging** with structured JSON output
- **Alert system** with webhook and email notifications
- **Configuration management** with environment-specific settings
- **Docker support** with multi-stage builds
- **CI/CD integration** with automated testing and deployment

### 🔧 **Easy Integration**
- **Simple decorators** for minimal code changes
- **Context managers** for flexible monitoring
- **MCP (Model Context Protocol) support** for tool monitoring
- **Framework agnostic** design
- **Extensive documentation** and examples

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install agent-sentinel

# Install with all dependencies
pip install agent-sentinel[monitoring,security]

# Install for development
pip install agent-sentinel[dev,test,docs]
```

### Basic Usage

```python
from agent_sentinel import sentinel, monitor

# Monitor an entire agent class
@sentinel
class CustomerServiceAgent:
    def __init__(self):
        self.name = "Customer Service Agent"
    
    # Monitor specific methods
    @monitor
    def handle_inquiry(self, user_input: str) -> str:
        # Your agent logic here
        return f"Response to: {user_input}"

# Use the agent
agent = CustomerServiceAgent()
response = agent.handle_inquiry("Hello, I need help with my order")
```

### Advanced Usage

```python
from agent_sentinel import AgentSentinel, secure_communication, secure_mcp_tool

# Initialize with configuration
sentinel = AgentSentinel(config_path="config.yaml")

# Secure communication wrapper
@secure_communication
class SecureChatAgent:
    def send_message(self, message: str):
        # Encrypted message sending
        pass
    
    def receive_message(self, message: str):
        # Validated message receiving
        pass

# MCP tool security
@secure_mcp_tool
def search_database(query: str):
    # Secure database search with validation
    pass
```

## 📋 Configuration

Create a configuration file (`config.yaml`):

```yaml
sentinel:
  agent_id: "production_agent"
  environment: "production"
  
  detection:
    enabled: true
    confidence_threshold: 0.8
    
    rules:
      sql_injection:
        enabled: true
        severity: "CRITICAL"
      xss_attack:
        enabled: true
        severity: "HIGH"
      prompt_injection:
        enabled: true
        severity: "HIGH"
    
    rate_limits:
      default_limit: 100
      default_window: 60
  
  logging:
    level: "INFO"
    format: "json"
    file: "logs/sentinel.log"
  
  alerts:
    webhook_url: "https://your-webhook-url.com"
    email:
      enabled: true
      smtp_server: "smtp.gmail.com"
      recipients: ["admin@company.com"]
```

## 🐳 Docker Support

### Production Image

```bash
# Build production image
docker build --target production -t agentsentinel/agent-sentinel:latest .

# Run with configuration
docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml agentsentinel/agent-sentinel:latest
```

### Development Image

```bash
# Build development image
docker build --target development -t agentsentinel/agent-sentinel:dev .

# Run with hot reload
docker run -p 8000:8000 -v $(pwd):/app agentsentinel/agent-sentinel:dev
```

## 🛠️ CLI Tools

Sentinel provides comprehensive command-line tools:

```bash
# Initialize configuration
agent-sentinel init --output config.yaml

# Validate configuration
agent-sentinel validate --config config.yaml --strict

# Start monitoring
agent-sentinel monitor --config config.yaml --daemon

# Show statistics
agent-sentinel stats --format json

# Run security checks
agent-sentinel security-check --output report.json

# Show version
agent-sentinel version
```

## 📚 API Reference

### Core Decorators

#### `@sentinel`
Monitors an entire agent class with comprehensive security and performance tracking.

```python
@sentinel
class MyAgent:
    def __init__(self):
        self.name = "My Agent"
    
    def process_input(self, data: str) -> str:
        return f"Processed: {data}"
```

#### `@monitor`
Monitors individual methods with detailed performance and security metrics.

```python
class MyAgent:
    @monitor
    def critical_method(self, input_data: str) -> str:
        # Method implementation
        return result
```

### Communication Security

#### `@secure_communication`
Secures communication channels with encryption and validation.

```python
@secure_communication
class SecureAgent:
    def send_message(self, message: str):
        # Encrypted message sending
        pass
    
    def receive_message(self, message: str):
        # Validated message receiving
        pass
```

#### `@secure_send` / `@secure_receive`
Individual send/receive security decorators.

```python
class CommunicationAgent:
    @secure_send
    def send_data(self, data: dict):
        # Secure data transmission
        pass
    
    @secure_receive
    def receive_data(self, data: dict):
        # Validated data reception
        pass
```

### MCP Tool Security

#### `@secure_mcp_tool`
Secures MCP (Model Context Protocol) tool calls with validation and monitoring.

```python
@secure_mcp_tool
def search_database(query: str) -> list:
    # Secure database search
    return results
```

#### `@secure_tool_call`
Monitors individual tool calls with security validation.

```python
@secure_tool_call
def file_operation(path: str, operation: str):
    # Secure file operations
    pass
```

### Context Managers

```python
from sentinel import AgentSentinel

# Using context manager for temporary monitoring
with AgentSentinel(config_path="config.yaml") as sentinel:
    # Your code here
    result = agent.process_data(input_data)
```

## 🔧 Advanced Configuration

### Custom Detection Rules

```yaml
detection:
  rules:
    custom_rule:
      enabled: true
      severity: "HIGH"
      patterns:
        - "malicious_pattern_1"
        - "malicious_pattern_2"
      action: "block"
```

### Rate Limiting

```yaml
rate_limits:
  default_limit: 100
  default_window: 60
  
  tools:
    database_query:
      limit: 50
      window: 60
    file_operation:
      limit: 20
      window: 60
```

### Alert Configuration

```yaml
alerts:
  webhook_url: "https://your-webhook-url.com"
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-app-password"
    recipients: ["admin@company.com"]
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install agent-sentinel[test]

# Run all tests
pytest

# Run with coverage
pytest --cov=agent_sentinel --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/security/
```

## 📊 Monitoring and Metrics

Sentinel provides extensive monitoring capabilities:

### Performance Metrics
- Method execution time
- Memory usage
- CPU utilization
- Network I/O

### Security Metrics
- Threat detection rate
- False positive rate
- Blocked attacks
- Security event distribution

### Business Metrics
- Agent usage patterns
- User interaction data
- Response quality metrics
- Operational efficiency

## 🔒 Security Features

### Threat Detection
- **SQL Injection**: Pattern-based detection with confidence scoring
- **XSS Attacks**: Cross-site scripting prevention
- **Command Injection**: Shell command injection detection
- **Path Traversal**: Directory traversal attack prevention
- **Prompt Injection**: AI-specific prompt manipulation detection
- **Data Exfiltration**: Sensitive data leak prevention

### Security Measures
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Abuse prevention with configurable limits
- **Encryption**: End-to-end communication encryption
- **Audit Logging**: Complete security event audit trail
- **Access Control**: Role-based access management

## 🏢 Enterprise Integration

### Monitoring Systems
- **Prometheus**: Metrics export for monitoring
- **Grafana**: Dashboard integration
- **Datadog**: APM and monitoring integration
- **New Relic**: Performance monitoring
- **Sentry**: Error tracking and alerting

### Logging Systems
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Splunk**: Enterprise log management
- **CloudWatch**: AWS logging integration
- **Azure Monitor**: Microsoft Azure monitoring

### Security Tools
- **SIEM Integration**: Security Information and Event Management
- **SOAR Platforms**: Security Orchestration, Automation, and Response
- **Vulnerability Scanners**: Integration with security scanning tools
- **Compliance Tools**: GDPR, SOC2, HIPAA compliance support

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sentinel/sentinel.git
cd sentinel

# Install development dependencies
pip install -e ".[dev,test,docs]"

# Run pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://docs.sentinel.dev](https://docs.sentinel.dev)
- **Issues**: [GitHub Issues](https://github.com/sentinel/sentinel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sentinel/sentinel/discussions)
- **Security**: [Security Policy](https://github.com/sentinel/sentinel/security/policy)

## 🙏 Acknowledgments

- Built with ❤️ for the AI community
- Inspired by enterprise security best practices
- Powered by modern Python technologies
- Supported by the open-source community

---

**Sentinel** - Protecting AI agents in production environments since 2024. 