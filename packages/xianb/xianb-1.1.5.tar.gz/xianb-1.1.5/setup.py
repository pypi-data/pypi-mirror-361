from setuptools import setup, find_packages

setup(
    name='xianb',
    version='1.1.5',
    author='jxjiang',
    author_email='723137901@qq.com',
    description='修复队列在等待时还持有锁的BUG',
    python_requires='>=3.8',
    install_requires=[],
    packages=find_packages()
)
