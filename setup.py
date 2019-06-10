from setuptools import setup, find_packages


setup(name='conifer',
      version='0.0.2.dev0',
      description='Library for loading configuration values from multiple sources',
      author='alex-dr',
      author_email='alexconway12@gmail.com',
      url='https://github.com/alex-dr/conifer',
      install_requires=[
          # License: MIT
          'jsonschema',
          # License: MIT
          'PyYAML',
      ],
      extras_require={
          'test': [
              'pytest',
              'pytest-mock',
              'tox',
          ],
      },
      packages=find_packages(),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
      ],
      keywords=[
          'config', 'configuration'
      ],
      )
