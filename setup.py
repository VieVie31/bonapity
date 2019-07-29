from setuptools import setup

setup(
    name='bonapity',
    version='0.1.4',
    description='Get a simple HTTP (GET) API with only this simple decorator : @bonapity !',
    long_description="""
# 👀 BONAPITY 👀

`bonAPIty` is a python3 package allowing you to create simple API (GET) 
for your functions without writting any complicated line of server code
and it's even simpler than Flask !

You are the 👨‍🍳, just do what you do the best : cook code !
don't loose your time to 💁, we do it for you... :)

By type hinting your code we cast 
the received inputs to the right type ! 
so don't worry about it... 😀
    """,
    long_description_content_type='text/markdown',
    url='http://github.com/VieVie31/bonapity',
    author='Olivier RISSER-MAROIX',
    author_email='orissermaroix@gmail.com',
    license='CC-BY',
    packages=['bonapity'],
    zip_safe=False
)

