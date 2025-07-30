from setuptools import setup, find_packages

setup(
    name='birddata',
    version='0.1.0',
    description='A custom bird classification dataset',
    author='Pratiksha Rawat',
    author_email='your@email.com',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
