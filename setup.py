from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in godomall_api_customization/__init__.py
from godomall_api_customization import __version__ as version

setup(
	name="godomall_api_customization",
	version=version,
	description="NHN naver commerce API connector",
	author="John Park",
	author_email="yuntan0@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
