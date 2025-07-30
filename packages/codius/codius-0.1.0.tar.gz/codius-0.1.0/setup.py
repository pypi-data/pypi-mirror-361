import os
import re

from setuptools import setup, find_packages

def get_version():
    with open(os.path.join("src", "codius", "__version__.py"), encoding="utf-8") as f:
        match = re.search(r'^__version__ = ["\']([^"\']+)["\']', f.read())
        if match:
            return match.group(1)
        raise RuntimeError("Version not found")

setup(
    name='codius',
    version=get_version(),
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,
    install_requires=[
        'exceptiongroup',
        'jinja2',
        'langgraph',
        'langchain',
        'langchain-openai',
        'py-dependency-injection>=1.0.0b3',
        'python-dateutil',
        'python-dotenv',
        'pyyaml',
        'prompt-toolkit',
        'rich',
        'tree-sitter==0.23.2',
        'tree-sitter-c-sharp',
    ],
    entry_points={
        'console_scripts': [
            'codius=codius.main:main',
        ],
    },
    author='David Runemalm',
    author_email='david.runemalm@gmail.com',
    description='A coding assistant for domain-driven design projects in ASP.NET Core.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/runemalm/codius-cli',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.9,!=3.13.*',
)
