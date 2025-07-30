from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='LXu_leetcode',
    version='0.3',
    packages=find_packages(),
    description='Reusable algorithm templates for LeetCode problems',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Zhihui Xu',
    author_email='your@email.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
