from setuptools import setup, find_packages


setup(name='conifer',
      version='0.0.1.dev0',
      description='Library for loading configuration values from multiple sources',
      author='alex-dr',
      install_requires=[
          'jsonschema'
      ],
      extras_require={
          'test': [
              'pytest'
          ],
      },
      packages=find_packages(),
      )
