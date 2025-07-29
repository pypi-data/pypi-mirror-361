from setuptools import setup, find_packages

setup(
    name='romiee',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
    author='Ramsha Noshad',
    author_email='your@email.com',
    description='A beginner-friendly web scraping kit',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/romiee',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'romiee=romiee.cli:run',
        ],
    },
)
