FROM tensorflow/tensorflow:1.6.0-devel-gpu-py3
COPY ./home/ /home/
RUN mkdir /usr/java \
&& cp -r /home/SySeVR/softdir/jdk1.8.0_161 /usr/java \
&& mkdir /usr/ant \
&& cp -r /home/SySeVR/softdir/apache-ant-1.9.14 /usr/ant \
&& rm -rf /etc/apt/sources.list \
&& cp -r /home/SySeVR/softdir/sources.list /etc/apt/ \
&& rm -rf /etc/apt/sources.list.d \
&& apt-get clean \
&& apt-get update \
&& rm -rf /etc/profile \
&& cp -r /home/SySeVR/softdir/profile /etc \
&& cd /home/SySeVR/softdir \
&& chmod +x env.sh \
&& ./env.sh \
&& apt-get install -y python-setuptools \
&& apt-get install -y python-dev \
&& apt-get install -y python-pip \
&& cd /home/SySeVR/softdir/py2neo-py2neo-2.0 \
&& python2 setup.py install \
&& cd /home/SySeVR/softdir/python-joern-0.3.1 \
&& python2 setup.py install \
&& apt-get install -y graphviz \
&& apt-get install -y libgraphviz-dev \
&& apt-get install -y pkg-config \
&& apt-get install -y python-igraph \
&& apt-get install -y python-virtualenv \
&& pip3 install xlrd \
&& pip3 install gensim==3.4 \
&& pip3 install pyyaml \
&& rm -rf /home/SySeVR/softdir   
