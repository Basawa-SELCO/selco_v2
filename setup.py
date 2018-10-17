# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import re, ast

# get version from __version__ variable in selco/__init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('selco/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

def parse_requirements(path, get_dependency_links = False):
	with open(path) as f:
		deps = f.read().strip().split('\n')
		if not get_dependency_links: return deps
		link_pattern = re.compile(r"(git)?\+?(git|https?):\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)")
		return [re.search(link_pattern, dep).group() for dep in deps if re.search(link_pattern, dep)]

setup(
	name='selco',
	version=version,
	description='Selco Customizations',
	author='SELCO',
	author_email='basawaraj@selco-india.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=parse_requirements('requirements.txt')
)
