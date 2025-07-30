from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='SyloraQ',
    version='3.1',
    packages=find_packages(),
    install_requires=[],
    author='SyloraQ',
    license="SyloraQ Software Agreement",
    author_email='syloraq.official@gmail.com',
    description='SyloraQ Python Module One Step Ahead',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SyloraQ/SyloraQ',
    classifiers=[  
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
    ],
)
