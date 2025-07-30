from setuptools import setup, find_packages

setup(
    name="guifrontend",
    version="0.1.2",  # 更新版本号
    author="xiao",
    description="A frontend client for the GUI data collection framework.",
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "websockets==12.0",
        "pillow==10.1.0",
        "pyautogui==0.9.54",
        "pyyaml==6.0.1",
        "async-timeout==4.0.3",
        "importlib-resources; python_version<'3.9'"
    ],
    entry_points={
        "console_scripts": [
            "gui=guifrontend.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)