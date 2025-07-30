# Agent Sentinel SDK

Enterprise-grade security monitoring SDK for AI agents with real-time threat detection, behavioral analysis, and comprehensive reporting capabilities.

## 🚀 Quick Start

### Installation

```bash
pip install agent-sentinel
```

### Basic Usage - Just 3 Lines of Code!

```python
from agent_sentinel import monitor, sentinel, monitor_mcp

# Monitor individual functions
@monitor
def my_agent_function():
    return "monitored function"

# Monitor entire classes
@sentinel
class MyAgent:
    def process_data(self, data):
        return data.upper()
    
    def analyze_threats(self):
        return "threat analysis"

# Monitor MCP tools
@monitor_mcp()
def my_mcp_tool():
    return "monitored MCP tool"
```

**✅ Verified Working** - All decorators have been thoroughly tested and are production-ready!

## 🆕 What's New in v0.1.9

- ✅ **Fully Tested Decorators**: All three decorators (`@monitor`, `@sentinel`, `@monitor_mcp`) verified working
- ✅ **Enhanced Class Monitoring**: Improved `@sentinel` decorator with real-time threat detection across all methods
- ✅ **Comprehensive Logging**: Structured JSON logging with performance metrics and threat analysis
- ✅ **Production Ready**: Successfully tested with real agents and MCP tools
- ✅ **Zero Configuration**: Works out of the box with sensible defaults
- ✅ **Enterprise Features**: Full threat detection, behavioral analysis, and reporting capabilities

## 📚 Available Decorators

**Agent Sentinel provides exactly 3 decorators for all your monitoring needs:**

### 1. `@monitor` - Function Monitoring
Monitor individual functions with comprehensive security analysis.

```python
from agent_sentinel import monitor

@monitor
def process_user_data(data: str) -> str:
    # Your agent logic here
    return data.upper()
```

**Features:**
- ✅ Input validation
- ✅ Behavior analysis
- ✅ Performance monitoring
- ✅ Security event detection
- ✅ Structured logging

### 2. `@sentinel` - Class-Level Monitoring
Monitor entire classes by automatically wrapping all public methods.

```python
from agent_sentinel import sentinel

@sentinel
class SecurityAgent:
    def analyze_threats(self, data):
        return "threat analysis"
    
    def generate_report(self, findings):
        return "security report"
    
    def _private_method(self):  # Not monitored (private)
        return "private"
```

**Features:**
- ✅ Monitors all public methods automatically
- ✅ Class-level security statistics  
- ✅ Session tracking
- ✅ Method call patterns
- ✅ Real-time threat detection across all methods

### 3. `@monitor_mcp` - MCP Tool Monitoring
Specialized monitoring for Model Context Protocol (MCP) tools.

```python
from agent_sentinel import monitor_mcp

@monitor_mcp()
def my_mcp_tool():
    return "monitored MCP tool"

# With custom configuration
@monitor_mcp(validate_inputs=True, validate_outputs=True)
def advanced_mcp_tool():
    return "advanced MCP tool"
```

**Features:**
- ✅ MCP-specific validation
- ✅ Tool call tracking
- ✅ Input/output sanitization
- ✅ MCP protocol compliance

---

**That's it! Just 3 decorators for all your AI agent security monitoring needs.**

## 🔧 Advanced Usage

### Custom Configuration

```python
from agent_sentinel import AgentSentinel

sentinel = AgentSentinel(
    config_dict={
        "agent_id": "custom_agent",
        "environment": "production",
        "detection": {
            "enabled": True,
            "confidence_threshold": 0.8
        },
        "logging": {
            "level": "INFO",
            "format": "json",
            "file": "logs/agent_sentinel.log"
        }
    }
)
```

### Event Handlers

```python
from agent_sentinel import AgentSentinel
from agent_sentinel.core.types import SecurityEvent

def custom_event_handler(event: SecurityEvent):
    print(f"Security event detected: {event.message}")
    # Send to external systems, trigger alerts, etc.

sentinel = AgentSentinel(agent_id="my_agent")
sentinel.add_event_handler(custom_event_handler)
```

## 📊 Monitoring & Reporting

### Security Events

The SDK automatically detects and logs security events:

- **Data Exfiltration Attempts**
- **Command Injection**
- **Privilege Escalation**
- **Behavioral Anomalies**
- **Input Validation Failures**
- **Performance Issues**

### Reports

Generate comprehensive security reports:

```python
from agent_sentinel import AgentSentinel

sentinel = AgentSentinel(agent_id="my_agent")

# Generate unified report
report_path = sentinel.generate_unified_report()

# Export events for external analysis
events = sentinel.export_events(format="json")

# Get security metrics
metrics = sentinel.get_metrics()
```

### Integration with W&B

The SDK integrates with Weights & Biases for tracing and monitoring:

```python
# Configure W&B integration in your config
config = {
    "weave": {
        "enabled": True,
        "project": "agent-sentinel",
        "entity": "your-username"
    }
}
```

## 🛡️ Security Features

### Threat Detection

- **Real-time threat analysis**
- **Pattern recognition**
- **Anomaly detection**
- **Input validation**
- **Output sanitization**

### Validation

- **Type checking**
- **Content validation**
- **Security rule enforcement**
- **Custom validation rules**

### Monitoring

- **Performance metrics**
- **Behavior analysis**
- **Session tracking**
- **Event correlation**

## 🔗 Integration

### With Intelligence Layer

Export events for AI-powered analysis:

```python
# Export for intelligence layer processing
export_data = sentinel.export_for_llm_analysis()
```

### With External Systems

```python
# Export events to external SIEM
events = sentinel.export_events(format="json")

# Send to external monitoring
sentinel.add_event_handler(external_monitoring_handler)
```

## 📈 Performance

The SDK is designed for high-performance production environments:

- **Minimal overhead** (< 1ms per function call)
- **Asynchronous processing**
- **Circuit breaker protection**
- **Resource management**
- **Scalable architecture**

## 🔧 Configuration

### YAML Configuration

```yaml
agent_id: "my_agent"
environment: "production"

detection:
  enabled: true
  confidence_threshold: 0.8

logging:
  level: "INFO"
  format: "json"
  file: "logs/agent_sentinel.log"

weave:
  enabled: true
  project: "agent-sentinel"
  entity: "your-username"
```

### Environment Variables

```bash
export AGENT_SENTINEL_CONFIG_PATH="config.yaml"
export AGENT_SENTINEL_AGENT_ID="my_agent"
export AGENT_SENTINEL_ENVIRONMENT="production"
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "your_agent.py"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-sentinel
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-sentinel
  template:
    metadata:
      labels:
        app: agent-sentinel
    spec:
      containers:
      - name: agent-sentinel
        image: agent-sentinel:latest
        env:
        - name: AGENT_SENTINEL_CONFIG_PATH
          value: "/app/config.yaml"
```

## 📚 Examples

See the `examples/` directory for comprehensive usage examples:

- Basic monitoring
- Advanced configuration
- Custom event handlers
- Integration patterns
- Deployment examples

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.agent-sentinel.com](https://docs.agent-sentinel.com)
- **Issues**: [GitHub Issues](https://github.com/agent-sentinel/sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/agent-sentinel/sdk/discussions)
- **Email**: support@agent-sentinel.com

---

**Agent Sentinel SDK** - Enterprise-grade security monitoring for AI agents 🛡️ 