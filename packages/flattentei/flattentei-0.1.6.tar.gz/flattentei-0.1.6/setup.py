from setuptools import setup
import os


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='flattentei',
    version='0.1.6',
    description='Transform tei xml to a simple standoff format',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://git.gesis.org/nlp/flatten-tei',
    author='Wolf Otto',
    author_email='wolfgang.otto@gesis.org',
    license='BSD 2-clause',
    packages=['flattentei'],
    install_requires=[
        "lxml>=4.9.1",
    ],
    entry_points={
        'console_scripts': [
            'flatten-tei-folder=flattentei.flatten_tei_folder:main',
        ]
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    )

