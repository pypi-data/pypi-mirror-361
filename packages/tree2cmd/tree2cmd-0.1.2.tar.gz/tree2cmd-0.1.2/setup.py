import os  
from setuptools import setup, find_packages

setup(
    name='tree2cmd',
    version='0.1.2',
    description='Convert ChatGPT/LLM-style folder tree text to real files and folders',
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type='text/markdown',
    author='AnJoMa',
    author_email='antonyjosephmathew1@gmail.com',
    url='https://github.com/ajmanjoma/tree2cmd',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tree2cmd=tree2cmd.cli:main',
        ],
    },
    include_package_data=True,
    install_requires=[
        # add dependencies here if needed
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
    ],
    python_requires='>=3.6',
)
