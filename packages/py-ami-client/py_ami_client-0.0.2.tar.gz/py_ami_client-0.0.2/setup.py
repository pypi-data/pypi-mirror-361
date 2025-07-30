from setuptools import find_packages, setup

setup(
    name='py-ami-client',
    version='0.0.2',
    license="MIT",
    description='Python Asterisk Management Interface Client',
    author='Radin-System',
    author_email='technical@rsto.ir',
    url='https://github.com/Radin-System/py-ami-client',
    install_requires=[
        "classmods==0.1.3",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)