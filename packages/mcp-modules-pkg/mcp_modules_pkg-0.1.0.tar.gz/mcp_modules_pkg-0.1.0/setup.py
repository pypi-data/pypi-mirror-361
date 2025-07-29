from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-modules-pkg",  # PyPI에서 고유한 이름으로 변경
    version="0.1.0",
    author="yepark",
    author_email="yepark@bitmango.com",
    description="통합된 DB connector, gspread 인증 파일, MCP 모듈(base invoker, mcp loggers) 패키지",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/mcp-modules-pkg/",
    project_urls={
        "dough": "https://gitlab.bitmango.com/services/dev/dough.git",
        "masterapi-credentials": "https://gitlab.bitmango.com/services/web/masterapi.datawave.co.kr.git",
        "mcp-agents": "https://gitlab.bitmango.com/services/work-with-ai/mcp-agents.git",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "llm",
        "llm-gemini",
        "gspread",
        "pandas",
        "pymongo",
        "psycopg2-binary",
        "sqlalchemy",
        "cryptography"
    ],
    # entry_points={
    #     'console_scripts': [
    #         # CLI 명령어가 필요하다면
    #         'mcp-db-tool=mcp_modules_pkg.db_connector.cli:main',
    #         'mcp-cred-tool=mcp_modules_pkg.credentials.cli:main',
    #     ],
    # },
    include_package_data=True,
    package_data={
        'mcp_modules_pkg': ['**/*.json'],
    },
)
