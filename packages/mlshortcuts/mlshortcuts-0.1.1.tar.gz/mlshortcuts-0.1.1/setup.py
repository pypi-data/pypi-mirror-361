from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='mlshortcuts',
    version='0.1.1',
    author='Ganesh Gaikwad',
    packages=find_packages(),
    install_requires=[
    ],

    entry_points={
        "console_scripts":[
            "mlshortcuts = mlshortcuts:info",
        ],
    },

    long_description=long_description,
    long_description_content_type='text/markdown',
)