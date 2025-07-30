from setuptools import setup, find_packages

setup(
    name='mpesa_c2b_sdk',              # your SDK/package name
    version='0.1.0',                          # version of your package
    description='A Python SDK for Safaricom Daraja C2B APIs', 
    long_description=open('README.md').read(), 
    long_description_content_type='text/markdown',
    author='Belam Muia',
    author_email='your@email.com',
    url='https://github.com/bmuia/mpesa_c2b_sdk.git',
    packages=find_packages(),                # auto-find all packages
    install_requires=[
        'requests>=2.20.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
