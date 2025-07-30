from setuptools import setup, find_packages

setup(
    name='shared-service',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
    ],
    description='A reusable Django shared service',
    author='Your Name',
    author_email='your@email.com',
    url='https://github.com/yourusername/shared-service',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)