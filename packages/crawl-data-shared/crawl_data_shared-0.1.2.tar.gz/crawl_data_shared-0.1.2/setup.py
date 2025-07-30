from setuptools import setup, find_packages
import os

# Read requirements
def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README
def read_readme():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return "Shared internal package for microservices"

setup(
    name='crawl-data-shared',
    version='0.1.2',
    packages=find_packages(),
    py_modules=['exceptions', 'constants', 'response', 'http_client', 'logger', 'error_handlers'],
    include_package_data=True,
    install_requires=read_requirements(),
    author='huydq2k1',
    author_email='huyydq01@gmail.com',
    description='Shared internal package for microservices',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/huydz2k1/crawl-data-app',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
    keywords='microservices, shared, utilities',
    project_urls={
        'Bug Reports': 'https://github.com/huydz2k1/crawl-data-app/issues',
        'Source': 'https://github.com/huydz2k1/crawl-data-app',
    },
)
