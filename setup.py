from setuptools import setup

import bonapity

with open('README.md') as readme:
    setup(
        name='bonapity',
        version=bonapity.__version__,
        description='Get a simple HTTP (REST) API with only this simple decorator : @bonapity !',
        long_description='bonAPIty is a python3 package allowing you to create simple API (GET) for your functions without writing any complicated line of server code and it is even simpler than Flask !',
        long_description_content_type='text/markdown',
        url='https://vievie31.github.io/bonapity/',
        author='Olivier RISSER-MAROIX',
        author_email='orissermaroix@gmail.com',
        license='CC-BY',
        packages=['bonapity'],
        zip_safe=False
    )


