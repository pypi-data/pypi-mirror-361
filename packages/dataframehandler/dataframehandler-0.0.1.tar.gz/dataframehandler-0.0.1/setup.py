from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 4 - Beta',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='dataframehandler',
  version='0.0.1',
  description='A very basic data frame analyzer',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Migara Vidanalage',
  author_email='vidanalagemigara@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='data frame', 
  packages=find_packages(),
  install_requires=[''] 
)
