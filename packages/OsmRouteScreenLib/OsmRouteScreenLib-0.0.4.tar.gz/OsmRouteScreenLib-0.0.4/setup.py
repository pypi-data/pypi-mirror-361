from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='OsmRouteScreenLib',
  version='0.0.4',
  author='Aleksandr Krasnov',
  author_email='akrasnov87@gmail.com',
  description='Open Street Map route screenshot',
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  install_requires=['mercantile', 'pycairo'],
  classifiers=[
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='osm route screenshot',
  python_requires='>=3.10'
)