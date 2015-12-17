from setuptools import setup

setup(
    name='acmcli',
    version='0.0.1',
    packages=['src.acm_api'],
    url='https://github.com/actics/acmcli',
    license='MIT',
    author='actics',
    author_email='alexander.lavrukov@gmail.com',
    description='Console client for ACM online judges',
    entry_points="""
        [console_scripts]
        acmcli=acmcli:main
    """,
    install_requires=['requests', 'lxml', 'html2text']
)
