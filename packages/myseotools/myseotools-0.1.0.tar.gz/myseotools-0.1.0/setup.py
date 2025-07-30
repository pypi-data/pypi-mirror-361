from setuptools import setup, find_packages

setup(
    name='myseotools',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'spacy',
        'lxml'
    ],
    author='Your Name',
    description='Simple and powerful SEO toolkit in Python',
    long_description=open('README.md').read(),
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
)
