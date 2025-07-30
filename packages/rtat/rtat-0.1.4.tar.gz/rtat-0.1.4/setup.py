from setuptools import setup, find_packages

setup(
    name='rtat',
    version='0.1.4',
    packages=find_packages(),
    install_requires=[],
    author='Pablo Yepes',
    author_email='yepes@rice.edu',
    description='A package to Analysis Proton Therapy Data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/pabloyepes/rtat',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
