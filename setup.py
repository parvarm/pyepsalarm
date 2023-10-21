from setuptools import setup

__version__ = '1.0.0'

setup(
    name='pyepsalarm',
    py_modules=["pyepsalarm"],
    version=__version__,
    description='A simple library to interface with EPS systems, built for use with Home-Assistant',
    author='Parv Arm',
    author_email='parvarm@outlook.fr',
    url='https://github.com/parvarm/pyepsalarm',
    download_url='https://github.com/parvarm/pyepsalarm',
    license='Apache 2.0',
    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],
    keywords=['eps', 'homiris', 'alarm', 'hass', 'home assistant'],
    packages=['pyepsalarm'],
    include_package_data=True,
    install_requires=['requests==2.1.0'],
)
