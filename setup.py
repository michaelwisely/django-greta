from setuptools import setup, find_packages

setup(name="django-greta",
      version="0.1",
      # url='http://github.com/michaelwisely/django-greta',
      license='BSD',
      description="A Django app for displaying Git repos",
      author='Michael Wisely',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=['setuptools',
                        'django>1.6,<1.7',
                        'PyYAML==3.11',
                        'pygments==2.0.2',
                        'dulwich==0.10.0',
                        'factory_boy==2.5.2',
                        'django-guardian==1.3',
                        'django-celery==3.1.16',
                        'jsonschema==2.5.1',
                        'mistune==0.7.1',
                        ],
      )
