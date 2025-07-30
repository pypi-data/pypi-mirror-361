"""
publishsubライブラリのセットアップスクリプト
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="publishsub",
    version="1.0.0",
    author="tikisan",
    author_email="s2501082@sendai-nct.jp",
    description="依存関係ゼロの軽量パブリッシュ/サブスクライブメッセージングライブラリ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tikipiya/publishsub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "Topic :: Communications",
    ],
    python_requires=">=3.7",
    install_requires=[],  # 依存関係ゼロ！
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    keywords="pubsub, publish, subscribe, messaging, event, observer, pertern",
    project_urls={
        "Bug Reports": "https://github.com/tikipiya/publishsub/issues",
        "Source": "https://github.com/tikipiya/publishsub",
    },
)