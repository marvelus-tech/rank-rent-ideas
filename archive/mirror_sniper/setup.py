"""Setup configuration for MirrorSniper package."""

from setuptools import find_packages, setup


setup(
    name="mirror_sniper",
    version="0.1.0",
    description="MirrorSniper - Solana copy trading bot MVP foundation",
    python_requires=">=3.11",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "sqlalchemy[asyncio]>=2.0.0",
        "aiosqlite>=0.19.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "click>=8.0.0",
        "rich>=13.0.0",
        "loguru>=0.7.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "solders>=0.18.0",
        "solana-py>=0.30.0",
        "httpx>=0.24.0",
        "python-dotenv>=1.0.0",
        "alembic>=1.12.0",
        "PyYAML>=6.0.0",
        "base58>=2.1.1",
    ],
    entry_points={
        "console_scripts": [
            "mirror-sniper=mirror_sniper.main:main",
        ]
    },
)
