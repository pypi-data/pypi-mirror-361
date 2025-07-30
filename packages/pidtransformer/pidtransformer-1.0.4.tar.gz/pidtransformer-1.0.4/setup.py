from setuptools import setup, find_packages

setup(
    name='pidtransformer',
    version='1.0.4',
    author='Architect & Gem',
    description='A Transformer architecture with internal PID control for stabilizing learning dynamics.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Kangmin22/PID-Transformer-PROJECT',
    packages=find_packages(include=["pidtransformer", "pidtransformer.*"]),
    include_package_data=True,
    install_requires=[
        'torch', 'scipy', 'numpy', 'matplotlib', 'tqdm',
        'pytest', 'scikit-learn', 'datasets', 'transformers', 'sentencepiece'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.9',
)
