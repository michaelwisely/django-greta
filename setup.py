from setuptools import setup, find_packages

setup(name="django-greta",
      version="1.0",
      # url='http://github.com/michaelwisely/django-greta',
      license='BSD',
      description="A Django app for displaying Git repos",
      author='Michael Wisely',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=['setuptools',
                        'django>=1.4',
                        'PyYAML',
                        'pygments',
                        'dulwich>=0.8.6',
                        ],
      )
