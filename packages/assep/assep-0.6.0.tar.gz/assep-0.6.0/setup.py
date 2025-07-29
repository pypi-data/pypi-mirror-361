from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    description = f.read()

setup(
    name='assep',
    version='0.6.0',
    description='Automações em Python para auxiliar estudos em sistemas elétricos de potência',
    author='Nathan Kelvi de Almeida Bueno',
    author_email='nathankelvi@gmail.com',
    url='https://github.com/nkbueno/ASSEP',
    packages=['assep'],
    install_requires=[
        'pandas',
        'numpy',
        'easygui',
        'plotly',
        'matplotlib',
        'seaborn',
        'xlsxwriter',
        'pyarrow',
        'bs4',
        'selenium',
        'datetime',
        'requests',
        'scipy',
        'python-docx',
        # adicione aqui outras dependências
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)
