# 📚 agentic-os Documentation

Welcome to the complete documentation for this repository. This documentation is automatically generated and maintained by Woden Docbot.

![Health: Healthy](https://img.shields.io/badge/Health-Healthy-green) ![Files Documented: 10](https://img.shields.io/badge/Files_Documented-10-blue) ![Coverage: 100](https://img.shields.io/badge/Coverage-100-green) ![Last Updated: 2026-07-09](https://img.shields.io/badge/Last_Updated-2026--07--09-gray)

## 🔗 Quick Links

[📂 skills](./skills/README.md) | [📂 src](./src/README.md)
[📋 Dependencies](./DEPENDENCIES.md)


---

> A modular TypeScript codebase organizing service implementations and skill documentation with colocated tooling, lifecycle helpers, and runtime entry points.
> A documentation-first repository that indexes skill implementations and exposes TypeScript-based skill source (including a task-manager skill and UI).



## 📖 Overview

agentic-os organizes self-contained service modules and skill documentation to make it straightforward to implement, run, and validate service-level behavior. The services directory hosts service implementations and supporting artifacts; the current service, loop-harness, includes a TypeScript implementation, a public API surface, filesystem-backed utilities, lifecycle helpers, and CLI/daemon entry points with colocated tests.

The skills directory is a documentation-level index for skill implementations and their source modules. The current task-manager skill documents its behavior and points to a TypeScript src/ submodule and a UI submodule. Together the services and skills areas let developers find implementation code, runtime entry points, and documentation grouped by service or skill.
agentic-os organizes and documents skill implementations alongside their TypeScript source. The repository's primary role is to provide a navigable documentation index for skills and to point developers to the corresponding TypeScript modules and UI assets. The current, documented example is a task-manager skill that includes a documentation index and a TypeScript src submodule.

The layout is intentionally hierarchical and scaffolded: a top-level skills container groups per-skill subdirectories (for example task-manager/), each containing documentation indices and a src/ folder that holds TypeScript modules and type definitions plus a UI submodule. Separately, a src/ folder at the repository root provides a namespace for future documentation topics (metropolis/), which is currently empty. Technology explicitly present in the repository is TypeScript.


### 🧩 Key Components

| Component | Purpose | Technologies |
| --- | --- | --- |
| **services (directory)** | Top-level container for service implementations and their supporting tooling; organizes services into subdirectories so each service is developed and tested independently. | `TypeScript` |
| **services/loop-harness** | A TypeScript service implementation with a public API surface, filesystem-backed utilities, lifecycle helpers, CLI and daemon entry points, and colocated tests to validate behavior. | `TypeScript` |
| **skills (directory)** | Documentation-level index that groups per-skill documentation subdirectories and points to each skill's source and type definitions. | `TypeScript` |
| **skills/task-manager** | Documentation and source for the task-manager skill; includes a TypeScript src/ submodule (index and type definitions) and a UI submodule to document and expose the skill implementation. | `TypeScript` |
| **skills** | Top-level documentation index that groups per-skill documentation subdirectories and points to each skill's source code and type definitions. | N/A |
| **task-manager** | A documented skill subdirectory that contains the documentation-level source index and a src/ submodule with TypeScript modules, type definitions, and a UI submodule representing the task-manager implementation. | `TypeScript` |
| **src** | A top-level container for documentation-related subdirectories (a namespace for additional docs); currently contains the metropolis/ subfolder but no root-level documentation files. | N/A |
| **metropolis** | A focused documentation topic folder under src/ intended to house documentation resources; currently present as scaffolding with no documented files. | N/A |




**Component Architecture:**

```mermaid
graph TD
    C0[services (directory)]
    C1[services/loop-harness]
    C2[skills (directory)]
    C3[skills/task-manager]
    C0[skills]
    C1[task-manager]
    C2[src]
    C3[metropolis]
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
A hierarchical documentation scaffold: top-level container directories group per-skill folders and documentation topics. Each skill folder contains a documentation index and a src/ subfolder for TypeScript source and UI, providing a predictable navigable structure.

### 💡 Use Cases

- ✦ Provide a discoverable index of skill implementations and their TypeScript source for developers
- ✦ Host and document a TypeScript-based task-manager skill alongside its UI and type definitions
- ✦ Serve as scaffolding and a predictable path for adding future topic-specific documentation (e.g., src/metropolis)



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

### [src](./src/README.md)
Holds source documentation and documentation-adjacent resources for the project; currently contains a single subdirectory for further documentation organization.


This directory currently contains no documentation files at the root level and serves primarily as a container for documentation-related subdirectories.

---

## 📊 Documentation Statistics

- **Files Documented**: 26
- **Directories**: 9
- **Coverage**: 100%
- **Last Updated**: 2026-07-18
- **Files Documented**: 10
- **Directories**: 8
- **Coverage**: 100%
- **Last Updated**: 2026-07-09

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