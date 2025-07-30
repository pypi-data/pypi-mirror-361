from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() #Gets the long description from Readme file

setup(
    name='ILegend',
    version='0.0',
    packages=find_packages(),
    install_requires=[
        'pandas','numpy', 'queue', 'traceback','os'
    ],
    author='Shanmukh raj MSS',
    author_email='satyaprabhamalireddi@gmail.com',
    description='ILegend Kernel usage',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
     project_urls={
           'Source Repository': 'https://github.com/ShanmukhEstrella/ILegend-MultiKernel-Jupyter' #replace with your github source
    }
)
