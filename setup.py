from importlib.metadata import entry_points
from setuptools import setup, find_packages

VERSION = '0.0.1'

with open('README.md', 'rt') as file:
    LONG_DESCRIPTION = file.read()

setup(
    name='spiral',
    version=VERSION,
    author='Amos Amissah',
    author_email='theonlyamos@gmail.com',
    description='Package for creating AI Agents using llms',
    long_description=LONG_DESCRIPTION,
    long_description_content_type = "text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests','python-dotenv','pydantic',
                      'serpapi', 'aiohttp', 'cohere',
                      'together', 'clarifai', 'google-search-results'
                    ],
    keywords='ai agent llm openai together clarifai cohere',
    project_urls={
        'Source': 'https://github.com/theonlyamos/spiral/',
        'Tracker': 'https://github.com/theonlyamos/spiral/issues',
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ]
)
