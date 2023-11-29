from setuptools import setup, find_packages
import os

with open("requirements.txt", "r") as requirements_file:
    install_requires = requirements_file.read().splitlines()

def read_readme():
    readme_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')
    with open(readme_file) as f:
        readme = f.read()
    return readme

setup(
    name = 'autodocumentation_python',
    version = '1.5.1',
    description='Automated documentationstring generation for python files within repositories, folders or for sinlge .py files.',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/StructuralNeurobiologyLab/autodoc',
    download_url='https://github.com/StructuralNeurobiologyLab/autodoc',
    author='Karl Heggenberger, Joergen Kornfeld.',
    author_email='karl.heggenberger@bi.mpg.de',
    packages = find_packages(),
    install_requires = install_requires,
    entry_points = {
    'console_scripts': [
        'autodoc = autodocumentation_python.main:execute',
    ]
}
)