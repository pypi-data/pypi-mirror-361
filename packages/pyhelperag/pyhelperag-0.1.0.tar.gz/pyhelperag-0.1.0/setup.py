from setuptools import setup, find_packages

setup(
    name='pyhelperag',
    version='0.1.0',
    packages=find_packages(),
    author='Your Name',
    author_email='you@example.com',
    description='A utility library with useful Python helpers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my_library',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
