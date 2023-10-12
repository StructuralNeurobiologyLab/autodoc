from setuptools import setup, find_packages

with open("requirements.txt", "r") as requirements_file:
    install_requires = requirements_file.read().splitlines()

setup(
    name = 'autodoc',
    version = '0.1',
    packages = find_packages(),
    install_requires = install_requires,
    entry_points = {
    'console_scripts': [
        'autodoc = code.main:main',
    ]
}
)