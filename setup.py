import os

from setuptools import setup, find_packages


def get_version():
    version_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'VERSION')
    v = open(version_path).read()
    if type(v) == str:
        return v.strip()
    return v.decode('UTF-8').strip()


readme_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)),
    'README.md',
)
long_description = open(readme_path).read()

try:
    version = get_version()
except Exception:
    version = '0.0.0-dev'

setup(
    name='samsungwsctl',
    version=version,
    author='Nick Whyte',
    author_email='nick@nickwhyte.com',
    description='A minimal alternative to samsungctl for controlling newer '
                'Samsung Smart TVs.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nickw444/samsungwsctl',
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
    install_requires=['websocket-client>=0.56.0,<0.57.0'],
    packages=find_packages(),
)
