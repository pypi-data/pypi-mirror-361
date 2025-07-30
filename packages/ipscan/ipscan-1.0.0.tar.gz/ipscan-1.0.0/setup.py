import setuptools

# 讀取長描述文件
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# 從 __init__.py 獲取版本信息
def get_version():
    with open("ipscan/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setuptools.setup(
    name="ipscan",
    version=get_version(),
    author="Wing",
    author_email="tomt99688@gmail.com",
    description="快速IP掃描工具 - 多線程 Ping 和 ARP 掃描",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Wing9897/ipscan.git",
    packages=setuptools.find_packages(),
    install_requires=[
        'ping3>=4.0.0',
        'tqdm>=4.60.0',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'fping=ipscan.ping:main',
            'farp=ipscan.arp:main',
        ]
    },
    keywords="ip scan ping arp network scanner",
)