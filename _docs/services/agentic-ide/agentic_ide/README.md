<details><summary>Directory Metadata (for smart change detection)</summary>

```json
{
  "doc_type": "directory_index",
  "directory_path": "_docs/services/agentic-ide/agentic_ide",
  "directory_hash": "17d55aa21719e51fad7f67b05debfcbebec621d00f347289d807188722bb1743",
  "file_count": 4,
  "file_hashes": {
    "__init__.py": "3fda113da29cf995",
    "config.py": "90c82266a2d38491",
    "main.py": "c7d135c85c29f25e",
    "models.py": "c3edfe0338a06fe0"
  }
}
```

</details>

[Documentation Home](../../../README.md) > [services](../../README.md) > [agentic-ide](../README.md) > [agentic_ide](./README.md) > **agentic_ide**

---

# 📁 agentic_ide

> **Purpose:** Host the Agentic IDE service modules: entry point, configuration, and data models, plus subpackages implementing the graph workflow, HTTP routes, and runtime services.
> 

![Organization: Hierarchical](https://img.shields.io/badge/Organization-Hierarchical-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Subdirectories](#subdirectories)
- [All Files](#all-files)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)

---

## Overview

This directory contains the Python implementation of the Agentic IDE service. At the root it provides four modules: __init__.py (package initialization), config.py (application configuration implemented with pydantic-settings integration), main.py (the FastAPI application entry point for the Agentic IDE), and models.py (data schemas used across the service). These root modules form the primary surface for running and configuring the Agentic IDE application and define the core types used by the workflow and HTTP layers.

Three subdirectories extend the root functionality. The graph/ subdirectory contains the LangGraph workflow components used by the Agentic IDE command loop (state schema, node implementations, and workflow assembly). The routes/ subdirectory provides HTTP route handlers, including a lightweight health-check endpoint and session lifecycle / agent command routes for interacting with the service. The services/ subdirectory includes runtime components such as an in-memory session store and a deterministic tool registry used at runtime. Together, the root modules and these subpackages implement a cohesive service where configuration and models inform the FastAPI entry point, the graph implements the agent workflow, routes expose HTTP access, and services provide runtime infrastructure.


### File Organization

Root-level files expose the package, configuration, application entry point, and data schemas. Feature-specific implementations are grouped into three subpackages (graph, routes, services) to separate workflow components, HTTP handlers, and runtime services. This keeps the FastAPI entry point and core types at the package root while isolating implementation details into focused subdirectories.

## 📂 Subdirectories

This directory contains the following subdirectories:

### [📁 graph](./graph/README.md)

**Purpose:** Contains the LangGraph workflow components for the Agentic IDE: state schema, node implementations, and workflow assembly used by the command loop.

![Files: 3](https://img.shields.io/badge/Files-3-blue)

---

### [📁 routes](./routes/README.md)

**Purpose:** Contains HTTP route handlers for the agentic IDE service, including a lightweight health-check endpoint and session lifecycle / agent command routes.

![Files: 2](https://img.shields.io/badge/Files-2-blue)

---

### [📁 services](./services/README.md)

**Purpose:** Holds runtime service components used by the agentic IDE, including an in-memory session store and a deterministic tool registry.

![Files: 2](https://img.shields.io/badge/Files-2-blue)

---
## 📂 All Files

| File | Type |
| --- | --- |
| [__init__.py](./__init__.py.md) | 🐍 Python |
| [config.py](./config.py.md) | 🐍 Python |
| [main.py](./main.py.md) | 🐍 Python |
| [models.py](./models.py.md) | 🐍 Python |

## Dependencies

### External Dependencies

| Dependency | Usage |
| --- | --- |
| `FastAPI` | Used by main.py as the web framework for the Agentic IDE application (entry point and route registration). |
| `pydantic-settings` | Used in config.py to provide application configuration models and settings integration. |

### Internal Dependencies

| Dependency | Usage |
| --- | --- |
| `graph subpackage` | Provides workflow components (state, nodes, assembly) used by the command loop and referenced by routes or services. |

## Architecture Notes

- Separation of concerns: root files provide entry, configuration, and core models while implementation details are grouped into graph, routes, and services subpackages.
- The FastAPI application is kept at the package root (main.py) to present a single entry point and to wire subpackage components (routes, services, graph) at startup.

---

## Navigation

**↑ Parent Directory:** [Go up](../README.md)
**🔗 Related:** [graph](./graph/README.md) • [routes](./routes/README.md) • [services](./services/README.md)

---

*Generated by Woden Docbot*