import setuptools
import re
import requests
from bs4 import BeautifulSoup

package_name = "MingChioY"
version = "1.0.5"


def curr_version():
    # 方法2：从官网获取版本号
    url = f"https://pypi.org/project/{package_name}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    latest_version = soup.select_one(".release__version").text.strip()
    return str(latest_version)


def get_version():
    # 从版本号字符串中提取三个数字并将它们转换为整数类型
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", curr_version())
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))

    # 对三个数字进行加一操作
    patch += 1
    if patch > 9:
        patch = 0
        minor += 1
        if minor > 9:
            minor = 0
            major += 1
    new_version_str = f"{major}.{minor}.{patch}"
    return new_version_str


def upload():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    with open('requirements.txt') as f:
        required = f.read().splitlines()

    setuptools.setup(
        name=package_name,
        version=version,
        author="MingChioY",  # 作者名称
        author_email="Chiyuan.jinggg@gmail.com",  # 作者邮箱
        description="Python tools MingChioY, updating!",  # 库描述
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://pypi.org/project/MingChioY/",  # 库的官方地址
        packages=setuptools.find_packages(),
        data_files=["requirements.txt"],  # 库依赖的其他库
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.6',
        install_requires=required,
        entry_points={
            'console_scripts': [
                'mingchioy = MingChioY.cli.main:main',
            ],
        }
    )


def write_now_version():
    print("Current VERSION:", get_version())
    with open("VERSION", "w") as version_f:
        version_f.write(get_version())


def main():
    try:
        upload()
        print(f"Upload package success {version}")
    except Exception as e:
        raise Exception("Upload package error", e)


if __name__ == '__main__':
    main()

