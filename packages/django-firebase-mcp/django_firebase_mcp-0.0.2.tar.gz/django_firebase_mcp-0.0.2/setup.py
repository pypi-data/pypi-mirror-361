from setuptools import setup, find_packages

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:  # Added encoding for cross-platform safety
    long_description = f.read()

setup(
    name='django-firebase-mcp',  # ✅ Make sure this name is unique on PyPI/Test PyPI
    version='0.0.2',  # ✅ Good practice: Increment this with each upload
    packages=find_packages(),
    description='A production-ready Django app implementing Firebase Model Context Protocol (MCP) server with 14 Firebase tools for AI agents. Features standalone agent, HTTP/stdio transport, LangChain integration, and complete Firebase service coverage (Auth, Firestore, Storage).',  # ✅ Keep it under 200 characters ideally
    author='Raghvendra Dasila',
    author_email='raghavdasila@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raghavdasila/django-firebase-mcp",
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',  # Optional: add this for clearer version state
        'Framework :: Django',              # Optional: helpful for discoverability
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    include_package_data=True,  # Optional: if you're including non-code files like templates, etc.
    install_requires=[
        # Add dependencies here if your package needs any (example)
        # 'firebase-admin>=6.0.0',
        # 'django>=3.2',
    ],
)
