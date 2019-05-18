from setuptools import setup


def readme():
    with open('./README.md') as f:
        return f.read()


setup(
    name='event_loop',
    version='0.1',
    author='mapogolions',
    author_email='ivanovpavelalex45@gmail.com',
    description='Simple event loop',
    license='LICENSE.txt',
    long_description=readme(),
    packages=['event_loop'],
    install_requires=['mood.event', 'pyuv']
)
