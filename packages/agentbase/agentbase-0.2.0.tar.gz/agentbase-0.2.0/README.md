# AgentBase 🤖

[![PyPI version](https://badge.fury.io/py/agentbase.svg)](https://badge.fury.io/py/agentbase)
[![Python versions](https://img.shields.io/pypi/pyversions/agentbase.svg)](https://pypi.org/project/agentbase/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/agentbase)](https://pepy.tech/project/agentbase)

**AgentBase** is a comprehensive open-source storage solution for AI agents with advanced memory management, experience replay, lifelong learning, and concept drift detection capabilities.

## 🚀 Features

- **🧠 Memory Management**: Fast-access cache with multiple eviction policies (LRU, LFU, TTL, Priority)
- **🔄 Experience Replay**: Reinforcement learning buffer with multiple sampling strategies
- **📚 Lifelong Learning**: Track model updates, mistakes, and corrections over time
- **📊 Metadata Logging**: Comprehensive training and experiment tracking
- **🔍 Concept Drift Detection**: Monitor data distribution changes with multiple algorithms
- **⚡ High Performance**: Thread-safe operations with efficient data structures
- **🎯 Easy Integration**: Simple API that works with any ML framework

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install agentbase
```

### With Optional Dependencies

```bash
# For machine learning features
pip install agentbase[ml]

# For visualization
pip install agentbase[viz]

# For all features
pip install agentbase[full]

# For development
pip install agentbase[dev]
```

### From Source

```bash
git clone https://github.com/bestagents/agentbase.git
cd agentbase
pip install -e .
```

## 🎯 Quick Start

```python
from agentbase import AgentBase

# Initialize AgentBase with default configuration
agent = AgentBase()

# Cache some data
agent.cache.set("user_preferences", {"theme": "dark", "lang": "en"})
cached_data = agent.cache.get("user_preferences")

# Store experience for reinforcement learning
experience = {
    "state": [1, 2, 3],
    "action": 0,
    "reward": 1.0,
    "next_state": [2, 3, 4],
    "done": False
}
agent.replay_buffer.add(**experience)

# Sample experiences for training
batch = agent.replay_buffer.sample(batch_size=32)

# Log training metadata
agent.logger.log_hyperparameters({"learning_rate": 0.001, "batch_size": 32})
agent.logger.log_metrics({"loss": 0.5, "accuracy": 0.95})

# Track model updates
agent.lifelong_learning.add_model_update(
    model_id="v1.0",
    performance={"accuracy": 0.95},
    metadata={"optimizer": "adam", "epochs": 100}
)

# Detect concept drift
new_data = [1.2, 2.3, 3.4, 4.5]
drift_detected = agent.drift_detector.detect_drift(new_data)
if drift_detected:
    print("Concept drift detected!")
```

## 🧩 Core Components

### MemoryCache
Fast-access storage with multiple eviction policies:

```python
from agentbase import MemoryCache

cache = MemoryCache(max_size=1000, eviction_policy="lru")
cache.set("key", "value", ttl=3600)  # TTL in seconds
value = cache.get("key")
```

### ExperienceReplayBuffer
Store and sample experiences for reinforcement learning:

```python
from agentbase import ExperienceReplayBuffer

buffer = ExperienceReplayBuffer(max_size=10000)
buffer.add(state=[1,2,3], action=0, reward=1.0, next_state=[2,3,4], done=False)
batch = buffer.sample(batch_size=32, method="uniform")
```

### LifelongLearningStore
Track model evolution and learning patterns:

```python
from agentbase import LifelongLearningStore

store = LifelongLearningStore()
store.add_model_update("v1.0", performance={"accuracy": 0.95})
store.record_mistake("incorrect_prediction", context={"input": [1,2,3]})
store.record_correction("fixed_logic", improvement=0.05)
```

### MetadataLogger
Comprehensive experiment tracking:

```python
from agentbase import MetadataLogger

logger = MetadataLogger(experiment_name="my_experiment")
logger.log_hyperparameters({"lr": 0.001, "batch_size": 32})
logger.log_metrics({"loss": 0.5, "accuracy": 0.95})
logger.export_data("experiment_results.json")
```

### ConceptDriftDetector
Monitor data distribution changes:

```python
from agentbase import ConceptDriftDetector

detector = ConceptDriftDetector(algorithm="ks_test")
detector.add_reference_data([1, 2, 3, 4, 5])
drift_detected = detector.detect_drift([1.5, 2.5, 3.5, 4.5])
```

## 🔧 Configuration

AgentBase supports flexible configuration:

```python
config = {
    "memory_cache": {
        "max_size": 10000,
        "eviction_policy": "lru",
        "ttl": 3600
    },
    "replay_buffer": {
        "max_size": 50000,
        "alpha": 0.6,  # For prioritized sampling
        "beta": 0.4
    },
    "drift_detector": {
        "algorithm": "ks_test",
        "threshold": 0.05,
        "window_size": 1000
    }
}

agent = AgentBase(config=config)
```

## 📊 Performance Monitoring

AgentBase includes built-in performance monitoring:

```python
# Get cache statistics
stats = agent.cache.get_statistics()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")

# Monitor memory usage
memory_info = agent.get_memory_usage()
print(f"Memory usage: {memory_info['total_mb']:.2f} MB")

# Export performance data
agent.export_performance_data("performance_report.json")
```

## 🔄 Persistence

Save and load agent state:

```python
# Save agent state
agent.save_state("agent_checkpoint.pkl")

# Load agent state
agent = AgentBase.load_state("agent_checkpoint.pkl")
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install agentbase[dev]

# Run tests
pytest tests/

# Run with coverage
pytest --cov=agentbase tests/
```

## 📚 Documentation

- **[API Reference](https://agentbase.readthedocs.io/)**
- **[Examples](https://github.com/bestagents/agentbase/tree/main/examples)**
- **[Tutorial](https://agentbase.readthedocs.io/tutorial)**

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python best practices
- Inspired by the need for robust AI agent storage solutions
- Thanks to all contributors and the open-source community

## 📈 Roadmap

- [ ] Advanced visualization dashboard
- [ ] Distributed storage backend
- [ ] Integration with popular ML frameworks
- [ ] Real-time monitoring and alerts
- [ ] Advanced drift detection algorithms
- [ ] Multi-agent coordination features

## 🔗 Links

- **Homepage**: https://bestagents.github.io/agentbase/
- **PyPI**: https://pypi.org/project/agentbase/
- **GitHub**: https://github.com/bestagents/agentbase
- **Documentation**: https://agentbase.readthedocs.io/
- **Issues**: https://github.com/bestagents/agentbase/issues

---

Made with ❤️ by the AgentBase team 