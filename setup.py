from setuptools import setup
from setuptools.command.install import install as _install


class PostInstall(_install):
    def run(self):
        import httpproxy
        httpproxy.copy_config()
        super(PostInstall, self).run()


setup(name='http_proxy',
      version='0.0.1',
      packages=['httpproxy', 'httpproxy.config', 'httpproxy.utils'],
      url='https://github.com/oleglpts/http-proxy',
      license='MIT',
      platforms='any',
      author='Oleg Lupats',
      author_email='oleglupats@gmail.com',
      description='Simple http-proxy',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      zip_safe=False,
      classifiers=[
            'Operating System :: POSIX',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5'
      ],
      entry_points={
          'console_scripts': [
              'http_proxy = httpproxy.__main__:main'
          ]
      },
      python_requires='>=3',
      package_data={'httpproxy': ['data']},
      install_requires=[
          'easy-daemon==0.0.3',
          'pycurl==7.43.0.3',
          'dnspython3==1.15.0',
          'pooled-ProcessMixIn==0.0.1'
      ],
      cmdclass={'install': PostInstall})
