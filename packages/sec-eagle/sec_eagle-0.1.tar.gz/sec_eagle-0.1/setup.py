from setuptools import setup, find_packages

setup(
    name='sec_eagle',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'beautifulsoup4',
        'numpy'
    ],
    python_requires='>=3.6',
    description='A Python package for parsing SEC data with XML and web scraping tools',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/secpy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)