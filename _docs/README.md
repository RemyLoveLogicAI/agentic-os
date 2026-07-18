# 📚 agentic-os Documentation

Welcome to the complete documentation for this repository. This documentation is automatically generated and maintained by Woden Docbot.

![Health: Healthy](https://img.shields.io/badge/Health-Healthy-green) ![Files Documented: 26](https://img.shields.io/badge/Files_Documented-26-blue) ![Coverage: 100](https://img.shields.io/badge/Coverage-100-green) ![Last Updated: 2026-07-18](https://img.shields.io/badge/Last_Updated-2026--07--18-gray)

## 🔗 Quick Links

[📂 services](./services/README.md) | [📂 skills](./skills/README.md)
[📋 Dependencies](./DEPENDENCIES.md)


---

> A modular TypeScript codebase organizing service implementations and skill documentation with colocated tooling, lifecycle helpers, and runtime entry points.



## 📖 Overview

agentic-os organizes self-contained service modules and skill documentation to make it straightforward to implement, run, and validate service-level behavior. The services directory hosts service implementations and supporting artifacts; the current service, loop-harness, includes a TypeScript implementation, a public API surface, filesystem-backed utilities, lifecycle helpers, and CLI/daemon entry points with colocated tests.

The skills directory is a documentation-level index for skill implementations and their source modules. The current task-manager skill documents its behavior and points to a TypeScript src/ submodule and a UI submodule. Together the services and skills areas let developers find implementation code, runtime entry points, and documentation grouped by service or skill.


### 🧩 Key Components

| Component | Purpose | Technologies |
| --- | --- | --- |
| **services (directory)** | Top-level container for service implementations and their supporting tooling; organizes services into subdirectories so each service is developed and tested independently. | `TypeScript` |
| **services/loop-harness** | A TypeScript service implementation with a public API surface, filesystem-backed utilities, lifecycle helpers, CLI and daemon entry points, and colocated tests to validate behavior. | `TypeScript` |
| **skills (directory)** | Documentation-level index that groups per-skill documentation subdirectories and points to each skill's source and type definitions. | `TypeScript` |
| **skills/task-manager** | Documentation and source for the task-manager skill; includes a TypeScript src/ submodule (index and type definitions) and a UI submodule to document and expose the skill implementation. | `TypeScript` |




**Component Architecture:**

```mermaid
graph TD
    C0[services (directory)]
    C1[services/loop-harness]
    C2[skills (directory)]
    C3[skills/task-manager]
    C0 --> C1
    C1 --> C2
    C2 --> C3
```

### 🏗️ Architecture

A modular, repository-organized layout: per-service subdirectories under services and per-skill subdirectories under skills. Each service is self-contained with implementation, public API, lifecycle helpers, CLI/daemon entry points, filesystem utilities, and colocated tests.

### 💡 Use Cases

- ✦ Develop and run the loop-harness service implementation (TypeScript) locally via CLI or as a daemon
- ✦ Author, document, and inspect skill implementations such as the task-manager and its UI/source modules
- ✦ Validate service behavior through colocated tests and use lifecycle helpers to start/stop services during development



### 🔧 Technologies


**Languages:** ![TypeScript: ](https://img.shields.io/badge/TypeScript--blue)

---

## 📑 Documentation Sections

### [services](./services/README.md)
Host service implementations and service-specific tooling; currently contains the loop-harness service implementation and its supporting artifacts.


The services directory is the top-level location for service implementations in this repository.

### [skills](./skills/README.md)
Top-level documentation index for skill implementations and their documentation; organizes and points to subdirectories that document individual skills and their source modules.

This directory serves as the documentation-level index for skill implementations and their associated source documentation.

![Files: 8](https://img.shields.io/badge/Files-8-blue)

---

## 📊 Documentation Statistics

- **Files Documented**: 26
- **Directories**: 9
- **Coverage**: 100%
- **Last Updated**: 2026-07-18

---

## 🧭 How to Navigate

> ℹ️ **INFO**
> Each directory has its own README.md with detailed information about that section. Use the breadcrumb navigation at the top of each page to navigate back to parent directories.

### Navigation Features

- **Breadcrumbs** - At the top of each page, showing your current location
- **Directory READMEs** - Each folder has a comprehensive overview
- **File Documentation** - Click through to individual file documentation
- **Search** - Use GitHub's search or your IDE's search functionality

---

## 🤖 About Woden DocBot

This documentation is automatically generated and kept up-to-date by Woden DocBot, an AI-powered documentation assistant. DocBot analyzes code on every pull request and updates documentation to reflect changes.

### Features

- **Automatic Updates** - Documentation updates on every PR
- **Comprehensive Coverage** - Files, functions, classes, and directories
- **Smart Navigation** - Breadcrumbs, related files, and parent links
- **AI-Powered** - Uses Azure GPT models for intelligent documentation generation

---

*Generated by Woden DocBot for agentic-os*