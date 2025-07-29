#!/usr/bin/env python3
"""
Notsql パッケージのセットアップ
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='notsql',
    version='1.0.0',
    author='tikisan',
    author_email='s2501082@sendai-nct.jp',
    description='JSONベースの簡易NoSQL DB（ファイル保存型）',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tikipiya/notsql',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    install_requires=[
        # 外部依存なし
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'notsql-example=notsql.example:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)