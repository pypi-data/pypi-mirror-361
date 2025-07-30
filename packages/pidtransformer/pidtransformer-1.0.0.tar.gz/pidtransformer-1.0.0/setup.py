# FILE: setup.py
from setuptools import setup, find_packages

# requirements.txt 파일에서 의존성 목록을 읽어옵니다.
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='pidtransformer',
    version='1.0.0',
    author='Architect & Gem',
    description='A Transformer architecture with internal PID control for stabilizing learning dynamics.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Kangmin22/PID-Transformer-PROJECT', # 당신의 GitHub URL로 변경하세요.
    packages=find_packages(), # pidtransformer 폴더 하위의 모든 패키지를 자동으로 찾아줍니다.
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.9',
)