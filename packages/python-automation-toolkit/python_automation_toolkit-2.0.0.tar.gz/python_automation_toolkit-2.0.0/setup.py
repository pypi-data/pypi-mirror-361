from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-automation-toolkit",
    version="2.0.0",
    author="Rohan Jadhav",
    author_email="rohan@example.com",
    description="A powerful cross-platform Python Automation Toolkit CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rohanjadhav03/python-automation-toolkit",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "requests",
        "schedule",
        "rich"
    ],
    entry_points={
        'console_scripts': [
            'pyautotool=automation.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Utilities",
    ],
    python_requires='>=3.6',
) 