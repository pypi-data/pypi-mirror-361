from setuptools import setup, find_packages

setup(
    name='dragdrag',
    version='0.1.0',
    description='局域网文件拖拽上传/下载/删除的Web应用',
    author='你的名字',
    author_email='your@email.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Werkzeug'
    ],
    entry_points={
        'console_scripts': [
            'dragdrag=dragdrag.app:main'
        ]
    },
    package_data={
        '': ['../templates/*.html'],
    },
    python_requires='>=3.6',
) 