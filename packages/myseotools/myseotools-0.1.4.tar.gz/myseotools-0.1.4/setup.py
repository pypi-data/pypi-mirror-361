from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='myseotools',
    version='0.1.4',  # Make sure this is incremented each time you upload
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'spacy',
        'lxml'
    ],
    author='Your Name',
    description='Simple and powerful SEO toolkit in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
    ],
    python_requires='>=3.7',
    entry_points={  # ✅ Entry point for CLI
        "console_scripts": [
            "myseo = myseotools.cli:main",
        ],
    },
)
