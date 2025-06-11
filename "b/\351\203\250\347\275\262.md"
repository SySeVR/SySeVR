WSL2 Ubuntu 环境部署说明
=======================

本文档基于仓库中的文件，总结在 WSL2(Ubuntu) 下部署 SySeVR 运行环境的大致步骤。

1. 安装 WSL2 与 Ubuntu
---------------------
在 Windows10/11 中启用 WSL2，并从 Microsoft Store 安装 Ubuntu 发行版。

2. 更新系统并安装基础工具
-------------------------
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install build-essential wget git curl -y
```

3. 安装 Java 与 Ant
------------------
SySeVR 使用 joern 0.3.1，需要 JDK 与 Ant。
```bash
sudo apt install openjdk-8-jdk ant -y
```
安装完成后，可通过 `java -version` 和 `ant -version` 检查是否成功。

4. 安装 Python 环境
------------------
SySeVR 同时依赖 Python2 与 Python3。
```bash
sudo apt install python2 python2-dev python3.6 python3-pip python3-dev -y
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py | sudo python2
```

5. 安装 Python 库
----------------
Python3 环境需要 TensorFlow 1.6 与 gensim 3.4 等库；Python2 环境需要 py2neo 2.0 等库。
```bash
# Python3
pip3 install tensorflow==1.6.0 gensim==3.4 xlrd pyyaml

# Python2
pip2 install py2neo==2.0 graphviz==0.8.4 pygraphviz==1.3
pip2 install python-igraph
```
如使用 GPU，可根据显卡驱动安装 TensorFlow 1.6 GPU 版本。

6. 部署 Neo4j 2.1.5
------------------
仓库自带 `neo4j-2.1.5`，也可从官方网站下载并解压到任意目录。
```bash
wget https://dist.neo4j.org/neo4j-community-2.1.5-unix.tar.gz
# 或直接使用仓库中的 neo4j-2.1.5
```
设置 `NEO4J_HOME` 环境变量，并按照 `neo4j-2.1.5/README.txt` 中的说明启动服务。

7. 安装并配置 Joern
------------------
仓库包含 `joern-0.3.1`，需在其目录中执行 `ant` 进行编译：
```bash
cd joern-0.3.1
ant
```
编译完成后可将可执行文件路径加入 `PATH` 或参照 `SySeVR_docker/docker_build/home/SySeVR/softdir/env.sh` 中的做法添加别名：
```bash
echo "alias joern='java -jar /路径/joern-0.3.1/bin/joern.jar'" >> ~/.bashrc
source ~/.bashrc
```

8. 安装其它依赖
--------------
```bash
sudo apt install graphviz libgraphviz-dev pkg-config -y
```

9. 初始化数据库目录
------------------
首次使用 Neo4j 时需初始化工作目录，可参考其文档执行 `neo4j start` 并设置默认用户名、密码。

10. 进一步操作
环境准备完成后，可参照 `Implementation/README.md` 中的步骤生成代码切片 (SeVC)、预处理数据并训练模型。
11. 训练模型并查看结果
--------------------
完成数据切片生成与预处理后，可执行以下命令训练模型：
```bash
cd Implementation/model
python3 bgru.py
```
训练结束后结果会保存在 `result/BGRU/BGRU` 文件中，可通过 `cat result/BGRU/BGRU` 查看精确率、召回率等指标。
