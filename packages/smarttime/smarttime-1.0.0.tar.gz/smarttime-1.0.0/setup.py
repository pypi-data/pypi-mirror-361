import io
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='smarttime',
    version='1.0.0',
    author='Sam Afzali',
    author_email='samafzalicode@gmail.com',
    description='The Ultimate Multilingual Time Engine for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/samafzali11/smarttime',  # آدرس گیت‌هاب
    license='CC BY-NC-ND 4.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(exclude=['tests', 'docs']),
    python_requires='>=3.7',
    install_requires=[
        'pytz>=2020.0',
        'pandas>=1.0.0'
    ],
    include_package_data=True,
    keywords='time parsing conversion formatting iso8601 durations persian english',
    project_urls={
        'Documentation': 'https://github.com/samafzali11/smarttime',
        'Source': 'https://github.com/samafzali/smarttime',
    },
)
