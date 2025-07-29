from setuptools import setup, find_packages

setup(
    name='website_crawler_sdk',
    version='0.1.1',
    packages=find_packages(),
    install_requires=['requests'],
    author='Pramod Choudhary',
    description='The official Python SDK for the Website Crawler API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://www.websitecrawler.org',
    python_requires='>=3.6',
)
