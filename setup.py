from setuptools import setup, find_packages

setup(
    name="agentic-os",
    version="0.1.0",
    python_requires=">=3.10",
    packages=find_packages(include=["packages", "packages.*"]),
    install_requires=[
        "anthropic>=0.40.0,<1.0.0",
        "langchain-anthropic>=1.0.0,<2.0.0",
        "langchain-core>=1.3.3,<2.0.0",
        "langgraph>=1.0.10,<2.0.0",
        "langgraph-checkpoint-sqlite>=3.1.0,<4.0.0",
    ],
)
