from setuptools import setup

setup(
    name='crpt1',
    version='1.0.2',
    author='exampleauthor',
    author_email='cmkha79@gmail.com',
    description='Lightweight system & cryptography utilities with helper functions.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://panel.cloudzy.com',
    packages=['crpt1'],
    include_package_data=True,
    install_requires=[
        'pycryptodome>=3.10'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
