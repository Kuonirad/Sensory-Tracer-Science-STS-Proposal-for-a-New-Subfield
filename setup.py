"""
Sensory Tracer Science (STS) - Setup Configuration

A scientific computing package for physics-based sensory tracer analysis
following rigorous academic and computational standards.
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    version_file = os.path.join('sensory_tracer_science', '__init__.py')
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '1.0.0'

# Read long description from README
def get_long_description():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def get_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="sensory-tracer-science",
    version=get_version(),
    author="STS Development Team",
    author_email="sts-dev@example.org",
    description="Physics-based framework for sensory tracer analysis with biological realism",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Kuonirad/Sensory-Tracer-Science-STS-Proposal-for-a-New-Subfield",
    
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    
    python_requires=">=3.8",
    install_requires=get_requirements(),
    
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'isort>=5.10.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'docs': [
            'sphinx>=4.5.0',
            'sphinx-rtd-theme>=1.0.0',
            'sphinxcontrib-bibtex>=2.4.0',
            'myst-parser>=0.17.0',
        ],
        'jupyter': [
            'jupyter>=1.0.0',
            'ipywidgets>=7.7.0',
            'matplotlib>=3.5.0',
        ]
    },
    
    entry_points={
        'console_scripts': [
            'sts-validate=sensory_tracer_science.tools:validate_framework',
            'sts-test=sensory_tracer_science.tools:run_tests',
        ],
    },
    
    package_data={
        'sensory_tracer_science': [
            'data/*.json',
            'data/*.csv', 
            'docs/*.md',
            'docs/*.rst',
        ],
    },
    
    include_package_data=True,
    zip_safe=False,
    
    keywords=[
        'physics', 'biophysics', 'sensory-analysis', 'tracers',
        'biocompatibility', 'information-theory', 'thermodynamics',
        'quantum-mechanics', 'electrophysiology', 'neuroscience'
    ],
    
    project_urls={
        'Documentation': 'https://sensory-tracer-science.readthedocs.io/',
        'Source': 'https://github.com/Kuonirad/Sensory-Tracer-Science-STS-Proposal-for-a-New-Subfield',
        'Tracker': 'https://github.com/Kuonirad/Sensory-Tracer-Science-STS-Proposal-for-a-New-Subfield/issues',
        'Wiki': 'https://github.com/Kuonirad/Sensory-Tracer-Science-STS-Proposal-for-a-New-Subfield/wiki',
    },
)