from setuptools import setup, find_packages

setup(
    name='crpt',
    version='1.0.0',
    author='CryptoUtils',
    author_email='support@cryptoutils.org',
    description='A lightweight cryptography utilities package for Python developers.',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/cryptoutils/crpt',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'crpt=crpt.loader:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Security :: Cryptography'
    ],
    keywords='crypto cryptography utils security encryption',
)
