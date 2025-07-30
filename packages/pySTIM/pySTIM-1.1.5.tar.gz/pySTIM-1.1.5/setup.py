from setuptools import setup

def load_requirements(filename='requirements.txt'):
	with open(filename, 'r') as file:
		return file.read().splitlines()
	
setup(
	name='pySTIM',
	version='1.1.5',
	description='A python package for spatial omics analysis',
	url='https://github.com/qiaoxy0/STIM',
	install_requires=load_requirements(),
)