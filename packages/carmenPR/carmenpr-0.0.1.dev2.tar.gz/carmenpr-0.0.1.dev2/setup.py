from setuptools import setup, find_packages

setup(
    name='carmenPR',
    version='0.0.1.dev2',
    description='Un paquete épico con funciones aleatorias para mis proyectos (y mucho odio hacia Carmen PR).',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='XPro (Danito360)',
    author_email='dani@duction.es',
    url='https://github.com/carmenPR/odio',
    packages=find_packages(),
    install_requires=[
        'colorama',
        'rich',
        'cowsay'
    ],
    keywords='hate utilities carmen humor epic insultos utils duction',
    license='LOVE LICENSE',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
