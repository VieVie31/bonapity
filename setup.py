from setuptools import setup

import bonapity

setup(
    name='bonapity',
    version=bonapity.__version__,
    description='Get a simple HTTP (REST) API with only this simple decorator : @bonapity !',
    long_description='bonAPIty is the simplest python (3.7) package allowing you to create API for your functions without writing any complicated line of server code ! See more [here](https://vievie31.github.io/bonapity/) !',
    long_description_content_type='text/markdown',
    url='https://vievie31.github.io/bonapity/',
    author='Olivier RISSER-MAROIX',
    author_email='orissermaroix@gmail.com',
    license='CC-BY',
    packages=['bonapity'],
    zip_safe=False
)


