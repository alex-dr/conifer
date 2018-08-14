from setuptools import setup, find_packages


setup(name='conifer',
      version='0.0.1.dev0',
      description='Library for loading configuration values from multiple sources',
      author='alex-dr',
      author_email='alexconway12@gmail.com',
      url='https://github.com/alex-dr/conifer',
      install_requires=[
          'jsonschema'
      ],
      extras_require={
          'test': [
              'pytest',
              'pytest-mock',
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
          'Topic :: Software Development :: Libraries',
      ],
      keywords=[
          'config', 'configuration'
      ],
      )
