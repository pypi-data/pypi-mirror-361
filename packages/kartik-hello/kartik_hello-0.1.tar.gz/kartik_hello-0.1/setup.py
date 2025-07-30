from setuptools import setup, find_packages

setup(
    name='kartik-hello',
    version='0.1',
    packages=find_packages(),
    author='Kartik Singh',
    description='A simple hello package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/kartik-hello',
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
