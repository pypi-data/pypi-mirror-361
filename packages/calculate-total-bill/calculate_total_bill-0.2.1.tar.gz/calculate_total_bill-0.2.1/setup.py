from setuptools import setup, find_packages

setup(
  name='calculate_total_bill',
  version='0.2.1',
  description='This is a simple Python package that calculates total bill amount.',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',
  author='Gopi',
  author_email=' x23306882@student.ncirl.ie',
  classifiers=[
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
],
  keywords='calculate_total_bill', 
  packages=find_packages(),
  python_requires=">=3.6"
)
