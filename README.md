# python_script
该项目是一些简单、常用的python脚本的集合
+ ssh_rsa

1. 简介：批量完成 ssh rsa 认证，目标主机的信息保存在hosts中，格式为 IP username password

2. 步骤：生成rsa openssh密钥，将私钥保存在 /root/.ssh/id_rsa，公钥保存在 /root/.ssh/id_rsa.pub；读取需要处理的主机，建立ssh连接；将公钥添加到目标服务器/root/.ssh/authorities，实现免密登录准备

3. Usage： python3 ssh_rsa.py 线程数
