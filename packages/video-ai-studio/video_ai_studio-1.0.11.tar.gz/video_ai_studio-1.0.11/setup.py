"""
AI Content Generation Suite - Consolidated Setup Script

This setup.py consolidates all packages in the AI Content Generation Suite
into a single installable package with optional dependencies.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Package metadata
PACKAGE_NAME = "video_ai_studio"
VERSION = "1.0.11"
AUTHOR = "donghao zhang"
AUTHOR_EMAIL = "zdhpeter@gmail.com"
DESCRIPTION = "Comprehensive AI content generation suite with multiple providers and services"
URL = "https://github.com/donghaozhang/veo3-fal-video-ai"

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, encoding="utf-8") as f:
        long_description = f.read()

# Read requirements from root requirements.txt
def read_requirements():
    """Read requirements from root requirements.txt file."""
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        with open(req_file) as f:
            return [
                line.strip() for line in f 
                if line.strip() and not line.startswith("#")
            ]
    return []

# Base requirements (core dependencies only)
install_requires = [
    "python-dotenv>=1.0.0",
    "requests>=2.31.0", 
    "typing-extensions>=4.0.0",
    "pyyaml>=6.0",
    "pathlib2>=2.3.7",
    "argparse>=1.4.0",
]

# Optional requirements organized by functionality
extras_require = {
    # Core AI Content Pipeline
    "pipeline": [
        "pyyaml>=6.0",
        "pathlib2>=2.3.7",
    ],
    
    # FAL AI Providers
    "fal": [
        "fal-client>=0.4.0",
        "httpx>=0.25.0",
    ],
    
    # Google Cloud Services
    "google": [
        "google-cloud-aiplatform>=1.38.0",
        "google-cloud-storage>=2.10.0",
        "google-auth>=2.23.0",
        "google-genai>=0.1.0",
        "google-generativeai>=0.8.0",
    ],
    
    # Text-to-Speech Services
    "tts": [
        "elevenlabs>=1.0.0",
    ],
    
    # Video Processing
    "video": [
        "moviepy>=1.0.3",
        "ffmpeg-python>=0.2.0",
    ],
    
    # Image Processing
    "image": [
        "Pillow>=10.0.0",
    ],
    
    # Development Tools
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "black>=22.0.0",
        "flake8>=4.0.0",
        "mypy>=1.0.0",
    ],
    
    # Jupyter/Notebook Support
    "jupyter": [
        "jupyter>=1.0.0",
        "ipython>=8.0.0",
        "notebook>=7.0.0",
        "matplotlib>=3.5.0",
    ],
    
    # MCP Server Support
    "mcp": [
        "mcp>=1.0.0",
    ],
}

# Convenience groups
extras_require["all"] = list(set(
    req for group in ["pipeline", "fal", "google", "tts", "video", "image", "mcp"] 
    for req in extras_require[group]
))

extras_require["providers"] = list(set(
    req for group in ["fal", "google"] 
    for req in extras_require[group]
))

extras_require["services"] = list(set(
    req for group in ["tts", "video", "image"] 
    for req in extras_require[group]
))

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(include=['packages', 'packages.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            # AI Content Pipeline
            "ai-content-pipeline=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
            "aicp=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "packages.core.ai_content_pipeline": [
            "config/*.yaml",
            "examples/*.yaml", 
            "examples/*.json",
            "docs/*.md",
        ],
        "packages.providers.fal.image_to_image": [
            "config/*.json",
            "docs/*.md",
            "examples/*.py",
        ],
        "packages.services.text_to_speech": [
            "config/*.json",
            "examples/*.py",
        ],
        "": [
            "input/*",
            "output/*",
            "docs/*.md",
        ],
    },
    zip_safe=False,
    keywords="ai, content generation, images, videos, audio, fal, elevenlabs, google, parallel processing, veo, pipeline",
    project_urls={
        "Documentation": f"{URL}/blob/main/README.md",
        "Source": URL,
        "Tracker": f"{URL}/issues",
        "Changelog": f"{URL}/blob/main/CHANGELOG.md",
    },
)