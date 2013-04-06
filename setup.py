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
                        'django>1.4,<1.5',
                        'PyYAML==3.10',
                        'pygments==1.6',
                        'dulwich>=0.8.6',
                        'factory_boy==1.2.0',
                        'django-guardian==1.0.4',
                        'django-celery==3.0.11',
                        'South==0.7.6',
                        ],
      )
