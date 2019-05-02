from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='jira-sync',
    version="1.0",
    description="Track and Sync github Issues, PR, PR_Reviews as Jira Tasks",
    author="Omkar Khatavkar",
    author_email="okhatavkar007@gmail.com",
    url="https://github.com/omkarkhatavkar/jirasync",
    py_modules=['jirasync'],
    install_requires=required,
    dependency_links=[
        'git+ssh://github.com/omkarkhatavkar/did/tarball/master#egg=did'
    ],
    packages=find_packages("jirasync"),
    entry_points='''
        [console_scripts]
        jirasync=jirasync:cli
    ''',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)

