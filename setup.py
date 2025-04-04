from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()
setup(
    name='cisco_netbox_onboarding',
    version='4.2.0',
    packages=find_packages(),
    install_requires=[
        'requests>=2.32.3',
        'pynetbox>=7.4.1',
        'genie>=25.2',
        'pyats>=25.2',
        'netmiko>=4.5.0',
        'dotenv>=0.9.9',
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)