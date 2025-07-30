from setuptools import find_packages, setup

setup(
    name='adestis-netbox-domain-management',
    version='1.0.0',
    description='ADESTIS Domain Management',
    url='https://github.com/an-adestis/ADESTIS-Netbox-Domain-Management',
    author='ADESTIS GmbH',
    author_email='pypi@adestis.de',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    license='GPL-3.0-only',
    keywords=['netbox', 'netbox-plugin', 'plugin'],
    package_data={
        "adestis_netbox_domain_management": ["**/*.html"],
        '': ['LICENSE'],
    }
)
