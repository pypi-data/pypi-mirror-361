import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="HierVS",  # 模块名称
    version="1.0.2",  # 当前版本
    author="shukaigu",  # 作者
    author_email="3160101168@zju.edu.cn",  # 作者邮箱
    description="a fully AI-driven virtual screening package",  # 模块简介
    long_description=long_description,  # 模块详细介绍
    long_description_content_type="text/markdown",  # 模块详细介绍格式
    packages=setuptools.find_packages(),  # 自动找到项目中导入的模块
    # 模块相关的元数据
    # package_data={
    #     'hierarchicalvs': ['**/*'],  # 指定要包含的文件类型
    # #     },
    # include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    # 依赖模块
    entry_points={
        'console_scripts': [
            'HierVS=HierVS.hierarchicalvs:hierarchicalvs',
        ],
    },
    install_requires=[
        'pandas'
    ],
    
)