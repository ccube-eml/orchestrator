from setuptools import setup, find_packages

requirements = [
    'click',
    'PyYAML',
    'logbook',
    'paramiko',
]

setup(
    name='orchestrator',
    version='',
    url='',
    license='',
    author='John Doe',
    author_email='john.doe@ccube.com',
    description='',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': ['ccube-orchestrator=orchestrator.__main__:cli'],
    }
)
