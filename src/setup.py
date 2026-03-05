from setuptools import setup

setup(
    name='muqattaat_lab',
    version='1.0',
    packages=['muqattaat_lab'],
    install_requires=[
        'langgraph>=0.1.0',
        'langchain-core>=0.1.0',
        'anthropic>=0.25.0',
        'pyarabic>=0.6.15',
        'arabic-reshaper>=3.0.0',
        'python-bidi>=0.4.2',
        'networkx>=3.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'scipy>=1.11.0',
        'rich>=13.0.0',
        'neo4j>=5.0.0',
        'pytest>=7.1.2'
    ],
    extras_require={
        'dev': ['pytest>=7.1.2']
    }
)
