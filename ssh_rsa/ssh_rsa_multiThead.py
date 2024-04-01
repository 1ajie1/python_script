import paramiko
import cryptography
import threading
import sys
import os
import pwd
# 函数 cryptography 创建rsa密钥
def create_rsa_key(comment, choise, home):
    if choise.lower() == 'y':
        print("正在创建rsa密钥")
        key = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        # 将私玥转换为openssh格式
        private_key = key.private_bytes(
            cryptography.hazmat.primitives.serialization.Encoding.PEM,
            cryptography.hazmat.primitives.serialization.PrivateFormat.OpenSSH,
            cryptography.hazmat.primitives.serialization.NoEncryption()
        )

        # 将私玥写入文件
        with open(home + "/.ssh/id_rsa", "w") as f:
            f.write(private_key.decode())

        # print(private_key.decode())
        # 将公钥转换为openssh格式
        public_key = key.public_key().public_bytes(
            cryptography.hazmat.primitives.serialization.Encoding.OpenSSH,
            cryptography.hazmat.primitives.serialization.PublicFormat.OpenSSH
        )

        # 将公钥写入文件
        with open(home + "/.ssh/id_rsa.pub", "w") as f:
            f.write(public_key.decode() + " " + comment)
        print("创建成功")
    else:
        with open(home + "/.ssh/id_rsa.pub", "r") as f:
            public_key = f.read().strip().encode()

    return public_key.decode() + " " + comment

# 写一个函数，创建ssh连接
def ssh_connect(hostname ,port, username, password):
    ssh = paramiko.SSHClient()
    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, port=port, username=username, password=password)
        return ssh
    except Exception as e:
        print("连接失败:", e)

# 多线程执行任务的类

class multiThread(threading.Thread):
    def __init__(self,hosts,public_key):
        threading.Thread.__init__(self)
        self.hosts = hosts
        self.public_key = public_key
        self.ssh = ssh_connect(hostname=hostname, port=port, username=username, password=password) 

    def run(self):
        try:
            for host in self.hosts:
                hostname = host['hostname']
                port = host['port']
                username = host['username']
                password = host['password']
                ssh = ssh_connect(hostname=hostname, port=port, username=username, password=password)

                # 创建ssh连接
                # 执行命令, 将public_key 写入 ~/.ssh/authorized_keys
                cmd = f"echo '{self.public_key}' >> ~/.ssh/authorized_keys"
                # cmd = f"echo python Test!!!"
                stdin, stdout, stderr = ssh.exec_command(cmd)

                if stdout.read().decode():
                    print("返回结果：",stdout.read().decode())

                if stderr.read().decode():
                    print("返回的错误信息：",stderr.read().decode())

                ssh.close()
                
                print(hostname ,":执行成功!!!","\n")
        except Exception as e:
            print(hostname ,":执行失败!!!","\n")
         

if __name__ == '__main__':
    # usesage : 通过命令行传入线程数，python ssh_rsa.py 10
    if len(sys.argv) != 3:
        print("请传入线程数")
        print("Usage: python3 ssh_rsa.py 线程数 是否重新生成openssh密钥（y/n）")
        exit()
    thread_num = int(sys.argv[1])
    # 获取主机名, hostname
    loginName = pwd.getpwuid(os.getuid())[0]
    hostname = os.uname().nodename
    comment = loginName + "@" + hostname
    home = os.path.expanduser('~')
    print(home)
    public_key = create_rsa_key(comment=comment, choise=sys.argv[2], home=home)

    hosts_result = []

    with open("ssh_rsa/hosts", "r") as f:
        hosts = f.readlines()
        hosts = [ str(host).strip().split() for host in hosts]
        for host in hosts:
            hostname, username, password = host[0], host[1], host[2]
            port = 22
            host = {"hostname": hostname, "port": port, "username": username, "password": password}
            hosts_result.append(host)

    # 根据线程数分配每个线程所处理的主机数
    sub_hosts_result = [hosts_result[i*len(hosts_result)//thread_num: (i+1)*len(hosts_result)//thread_num] for i in range(thread_num)]
    print(sub_hosts_result)
    threads = []
    for host in sub_hosts_result:
        t = multiThread(hosts=host, public_key=public_key)
        threads.append(t)

    for i in range(len(threads)):
        threads[i].start()
        threads[i].join()

    print("执行完毕")    
    