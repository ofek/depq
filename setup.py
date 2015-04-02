from setuptools import setup, find_packages

with open('README.rst', 'r') as infile:
    read_me = infile.read()

setup(
    packages=find_packages(),

    name='depq',
    version='1.1.0',
    description='Double-ended priority queue',
    long_description=read_me,
    author='Ofek Lev',
    author_email='ofekmeister@gmail.com',
    maintainer='Ofek Lev',
    maintainer_email='ofekmeister@gmail.com',
    url='https://github.com/Ofekmeister/depq',
    download_url='https://github.com/Ofekmeister/depq',
    license='MIT',
    platforms=None,

    keywords=[
        'double ended priority queue',
        'depq',
        'priority queue',
        'collections',
        'abstract data types',
    ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
