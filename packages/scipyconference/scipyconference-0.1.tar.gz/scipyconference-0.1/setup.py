from distutils.core import setup

setup(name='scipyconference',
      version='0.1',
      description='SciPy Conference',
      author='SciPy Conference Organizers',
      include_package_data=True,
      package_data={'scipyconference': ['puns.json']},
      install_requires=[
          'numpy',
          'astropy',
          'pandas',
      ]
      )
