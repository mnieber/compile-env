from setuptools import find_packages, setup

setup(name='compile-env',
      version='0.3.0',
      description=
      'Solve the problem that environment variables are not interpolated by docker-compose',
      url='https://github.com/mnieber/compile-env',
      download_url='https://github.com/mnieber/compile-env/tarball/0.3.0',
      author='Maarten Nieber',
      author_email='hallomaarten@yahoo.com',
      license='MIT',
      packages=find_packages(),
      entry_points={'console_scripts': [
          'compile-env=compile_env.__init__:main',
      ]},
      data_files=[],
      install_requires=["PyYAML", "expandvars>=0.6.0", "six"],
      zip_safe=False)
