from setuptools import setup, find_packages

version = '0.0.2'

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ct_mail_handler',
    version=version,
    author='Shatrugna Rao Korukanti',
    author_email='shatrugna_korukanti@tecnics.com',
    description='Custom mail function and middleware to send logs to a mail server',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    install_requires=[
        'requests',
    ],
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)