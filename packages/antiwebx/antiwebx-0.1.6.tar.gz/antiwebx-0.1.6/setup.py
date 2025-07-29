from setuptools import setup, find_packages

setup(
    name='antiwebx',
    version='0.1.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'selenium>=4.0.0',
    ],
    author='AntifiedNull',
    description='Run headless Chrome via Selenium on Termux/Pydroid',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
)
