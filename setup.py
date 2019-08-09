from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='jirasync',
    version="1.1",
    description="Track and Sync github Issues, PR, PR_Reviews as Jira Tasks",
    author="Omkar Khatavkar",
    author_email="okhatavkar007@gmail.com",
    url="https://github.com/omkarkhatavkar/jirasync",
    install_requires=required,
    dependency_links=[
        'git+ssh://github.com/omkarkhatavkar/did/tarball/master#egg=did'
    ],
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    packages=find_packages(
        exclude=[
            "tests",
            "tests.*",
            "docs",
            "docs.*",
            "build",
            "build.*",
            "img",
            "img.*",
            "scripts",
            "scripts.*",
        ]
    ),
    entry_points={"console_scripts": ["jirasync=jirasync.cli:cli"]},
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
