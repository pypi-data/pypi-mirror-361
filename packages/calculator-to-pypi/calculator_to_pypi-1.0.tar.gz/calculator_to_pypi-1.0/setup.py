from setuptools import setup, find_packages

setup(
    name='calculator_to_pypi',
    version='1.0',
    license='MIT',
    author="SpiralTrain",
    author_email='spiraltrain@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    keywords='calculator project'
)
