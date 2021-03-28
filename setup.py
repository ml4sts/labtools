from setuptools import setup

setup(name='labtools',
      version='0.1',
      description='',
      url='',
      author='Sarah M Brown',
      author_email='brownsarahm@uri.edu',
      license='MIT',
      packages=['labtools'],
      zip_safe=False,
      include_package_data = True,
      install_requires=[''],
      entry_points = {
        'console_scripts': ['labnews=labtools.labnews:new_lab_news',
                            'newmember=labtools.newmember:new_member']}
     )
