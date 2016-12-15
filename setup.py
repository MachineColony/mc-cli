from setuptools import setup, find_packages


setup(
    name='mc-cli',
    version='0.0.4',
    description='Machine Colony command line tools',
    url='https://github.com/machinecolony/mc-cli',
    author='Machine Colony',
    author_email='francis@machinecolony.com',
    license='MIT',

    packages=find_packages(),
    install_requires=[
        'click',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        mc=mc_cli:cli
    ''',
)