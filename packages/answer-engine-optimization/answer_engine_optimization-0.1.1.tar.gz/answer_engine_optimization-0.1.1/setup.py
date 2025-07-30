from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='answer_engine_optimization',
    version='0.1.1',
    description='Answer Engine Optimization (AEO) toolkit for Python-based websites',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='SuperSharpAI.com',
    author_email='python@supersharpai.com',
    url='https://supersharpai.com/answer-engine-optimization-toolkit',
    packages=find_packages(),
    install_requires=['beautifulsoup4'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
)
