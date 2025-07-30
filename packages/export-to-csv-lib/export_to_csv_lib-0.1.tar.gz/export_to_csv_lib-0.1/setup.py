from setuptools import setup, find_packages

setup(
  name='export_to_csv_lib',
  version='0.1',
  description='This is python library to export the table data to csv.',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',
  author='Vivek',
  author_email=' x23324902@student.ncirl.ie',
  classifiers=[
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
],
  keywords='export_to_csv_lib', 
  packages=find_packages(),
  python_requires=">=3.6"
)
