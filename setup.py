from setuptools import setup

import bonapity

with open('README.md') as readme:
    setup(
        name='bonapity',
        version=bonapity.__version__,
        description='Get a simple HTTP (REST) API with only this simple decorator : @bonapity !',
        long_description=f"{readme.read()}\n---------------------\n🚧: still in 👷 🏗 ⚠️, already great features implemented, but the official git is not still openned... stay tuned ! 😃 🎞🎞🎞 ",
        long_description_content_type='text/markdown',
        url='https://vievie31.github.io/bonapity/',
        author='Olivier RISSER-MAROIX',
        author_email='orissermaroix@gmail.com',
        license='CC-BY',
        packages=['bonapity'],
        zip_safe=False
    )

