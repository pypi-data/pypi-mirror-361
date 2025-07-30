"""
Setup script for MCP Agent System
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "MCP Agent System - A Python SDK for MCP tool integration with LLM providers"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="mcp-agent-system",
    version="0.1.0",
    author="Observee",
    author_email="support@observee.ai",
    description="A Python SDK for MCP tool integration with LLM providers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/observee/mcp-agent-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
        ],
        "embedding": [
            "fastembed>=0.1.0",
        ],
        "cloud": [
            "pinecone-client>=2.0.0",
            "pinecone-text>=0.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-chat=observee_agents.cli:main",
        ],
    },
    keywords="mcp agent llm anthropic openai gemini tools",
    project_urls={
        "Bug Reports": "https://github.com/observee/mcp-agent-system/issues",
        "Source": "https://github.com/observee/mcp-agent-system",
        "Documentation": "https://docs.observee.ai/mcp-agent-system",
    },
) 