SySeVR WSL2 部署与训练指南
=======================

本文档基于仓库中的文件，提供在 Windows 下使用 WSL2(Ubuntu) 部署 SySeVR 的完整步骤，并说明如何训练模型和查看结果。

## 1. 安装 WSL2 与 Ubuntu
在 Windows10/11 中启用 WSL 功能，升级为 WSL2，然后从 Microsoft Store 安装 Ubuntu 发行版。

## 2. 更新系统并安装基础工具
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install build-essential wget git curl p7zip-full -y
```

## 3. 安装 Java 与 Ant
SySeVR 需要 JDK8 与 Ant 构建工具。
```bash
sudo apt install openjdk-8-jdk ant -y
java -version
ant -version
```

## 4. 安装 Python 环境
SySeVR 同时依赖 Python2 与 Python3。
```bash
sudo apt install python2 python2-dev python3.6 python3-pip python3-dev -y
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py | sudo python2
```

## 5. 安装 Python 库
```bash
# Python3
pip3 install tensorflow==1.6.0 gensim==3.4 xlrd pyyaml

# Python2
pip2 install py2neo==2.0 graphviz==0.8.4 pygraphviz==1.3
pip2 install python-igraph
```
如需 GPU，请根据显卡驱动安装 TensorFlow 1.6 GPU 版本。

## 6. 部署 Neo4j 2.1.5
仓库已包含 `neo4j-2.1.5`，也可从官网下载安装。
```bash
wget https://dist.neo4j.org/neo4j-community-2.1.5-unix.tar.gz
# 或直接使用仓库中的 neo4j-2.1.5
```
解压后设置 `NEO4J_HOME` 环境变量并启动：
```bash
export NEO4J_HOME=/路径/neo4j-2.1.5
$NEO4J_HOME/bin/neo4j start
```
首次启动需设置默认用户名和密码。

## 7. 安装并配置 Joern
仓库包含 `joern-0.3.1`，需要在其目录执行 `ant` 构建。
```bash
cd joern-0.3.1
ant
```
可将可执行文件加入 `PATH` 或按照 `SySeVR_docker/docker_build/home/SySeVR/softdir/env.sh` 设置别名：
```bash
echo "alias joern='java -jar /路径/joern-0.3.1/bin/joern.jar'" >> ~/.bashrc
source ~/.bashrc
```

## 8. 安装其它依赖
```bash
sudo apt install graphviz libgraphviz-dev pkg-config -y
```

## 9. 准备数据集
在 `Program data` 目录下存放有 NVD 和 SARD 数据集压缩包。
```bash
cd "Program data/NVD" && 7z x NVD.7z
cd "Program data/SARD" && 7z x SARD.7z
```
解压后的源码文件将供后续脚本处理。

## 10. 生成 SeVC 切片
根据 `Implementation/README.md`，依次执行以下脚本：
```bash
# 1) 使用 joern 解析源码
joern --script joern/joernParse.sc --params 'src=源码目录'

# 2) 生成 CFG、PDG 等中间结果
python2 Implementation/source2slice/get_cfg_relation.py
python2 Implementation/source2slice/complete_PDG.py
python2 Implementation/source2slice/access_db_operate.py
python2 Implementation/source2slice/points_get.py
python2 Implementation/source2slice/extract_df.py
python2 Implementation/source2slice/dealfile.py
python2 Implementation/source2slice/make_label_sard.py  # 或 make_label_nvd.py
python2 Implementation/source2slice/data_preprocess.py
```
上述脚本将得到带标签的切片文件。

## 11. 数据预处理
在 `Implementation/data_preprocess` 目录下运行：
```bash
python3 create_hash.py
python3 delete_list.py
python3 process_dataflow_func.py
python3 create_w2vmodel.py
python3 get_dl_input.py
python3 dealrawdata.py
```
这些步骤会生成用于训练的向量文件。

## 12. 训练模型并查看结果
进入模型目录运行训练脚本：
```bash
cd Implementation/model
python3 bgru.py
```
训练结束后，结果保存在 `result/BGRU/BGRU`。可通过
```bash
cat result/BGRU/BGRU
```
查看精确率、召回率等指标。

至此，SySeVR 的部署与训练流程完成。
