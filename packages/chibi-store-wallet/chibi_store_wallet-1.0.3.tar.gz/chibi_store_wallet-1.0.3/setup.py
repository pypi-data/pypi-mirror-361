from setuptools import setup, find_packages

setup(
    name='chibi_store_wallet',
    version='1.0.3',
    packages=find_packages(),
    install_requires=['requests'],
    author='PARK',
    author_email='parkontop07@gmail.com',
    description='Redeem TrueMoney gift via Python',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/chibi-redeem',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)