# Agent Sentinel

**Enterprise Security Monitoring SDK for AI Agents**

**Secure any AI agent in just 3 lines of code** - Real-time threat detection, behavioral analysis, and comprehensive reporting with zero-config deployment.

```python
from agent_sentinel import monitor, monitor_mcp

@monitor
def my_function(): pass

@monitor_mcp()
def my_mcp_tool(): pass
```

---

## 🚀 **3 Lines to Secure Any Agent**

### **Simple Integration**
```python
from agent_sentinel import monitor, monitor_mcp

@monitor
def process_user_input(user_data: str) -> str:
    return f"Processed: {user_data}"

@monitor_mcp()
def search_web(query: str) -> dict:
    return {"results": "web search results"}
```

**That's it!** Your agent is now protected against 20+ threat types with enterprise-grade monitoring.
