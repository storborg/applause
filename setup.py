from setuptools import setup


setup(name="applause",
      version='0.1',
      description="Applaud closing bugs.",
      long_description=open('README.rst').read(),
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='git github stats dashboard issues bug tracker',
      author='Scott Torborg',
      author_email='scott@cartlogic.com',
      url='http://github.com/storborg/applause',
      install_requires=['configobj', 'github2'],
      license='MIT',
      packages=['applause'],
      entry_points=dict(console_scripts=['applause=applause:main']),
      zip_safe=False)
