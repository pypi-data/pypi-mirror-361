from setuptools import setup, find_packages

setup(
    name='uploadi',
    version='0.6',
    description='Приложение для загрузки проектов python',
    long_description=open('./README.md', encoding='utf8').read(),
    packages=find_packages(),
    requires=[
        'twine',
        'setuptools'
    ],
    entry_points={
        'console_scripts': [
            'uploadi=uploadi.uploadi:uploadi',
        ],
    },
)
