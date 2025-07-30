from setuptools import setup, find_packages

setup(
    name='xa_izipy',
    version='0.0.1',
    author='Rigew',
    author_email='admin@atomgg.pro',
    description='Упрощает какие-то функции',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
