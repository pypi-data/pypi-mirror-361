from setuptools import setup, find_packages

setup(
    name='Commitly-cli',
    version='1.0.4',
    author='Kouya Tosten',
    author_email='kouyatosten@gmail.com',
    description='CLI tool to generate structured Git commit messages using AI.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Tostenn/Commitly-CLI',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'rich==13.7.1',
        "commitly==3.0.3",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Version Control',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'Commitly-CLI=CommitlyCLI.__main__:main',
        ],
    },
)
# rd -Path "C:\Path\To\Directory" -Recurse -Force
