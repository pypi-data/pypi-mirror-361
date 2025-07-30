from setuptools import setup, find_packages

setup(
    name='ashok-ll',  
    version='0.1.0',
    author='Ashok Bongu',
    author_email='bonguashok86@example.com',
    description='A Python package for Linked List operations by Ashok',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),  
    install_requires=[],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
