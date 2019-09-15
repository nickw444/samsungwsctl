import os

from setuptools import setup

readme_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)),
    'README.md',
)
long_description = open(readme_path).read()

setup(
    name='samsungwsctl',
    version='1.0.2',
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
    install_requires=[
        'websocket-client~=0.56.0',
        'requests~=2.22.0'
    ],
    py_modules=['samsungwsctl']
)
