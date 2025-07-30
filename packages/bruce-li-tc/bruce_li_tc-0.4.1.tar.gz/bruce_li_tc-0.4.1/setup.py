from setuptools import setup, find_packages
# setup.py 最顶部添加
import sys
import io
import re
def get_version():
    with open("src/bruce_li_tc/_version.py") as f:
        return re.search(r'__version__ = "(.*?)"', f.read()).group(1)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
setup(
    name='Bruce_li_tc',
    version=get_version(),
    description='A versatile utility library by Bruce Li',
    author='Bruce Li',
    author_email='bruce.li@example.com',
    packages=find_packages(exclude=["venv", "venv.*", "*.venv", "*.venv.*"]),
    include_package_data=True,
    exclude_package_data={
        '': ['venv', '.venv', 'env', '*.pyc', '__pycache__'],
    },
    install_requires=[],
    extras_require={
        'excel': ['openpyxl'],
        'async': ['aiohttp'],
        'loguru': ['loguru']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)