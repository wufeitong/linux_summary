# -*- coding:utf-8 -*-
import os
import re
from stat import S_ISDIR
from time import sleep
import paramiko


class RemoteConnect:
    def __init__(self,ip,port,username,password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.trans = paramiko.Transport((self.ip, self.port))
        self.trans.connect(username=self.username, password=self.password)

    # 建立ssh连接
    def ssh_connect(self):
        self.channel = self.trans.open_session()
        self.channel.get_pty()
        self.channel.invoke_shell()
        return self.channel

    # 断开连接
    def ssh_close(self):
        if self.channel:
            self.channel.close()
        if self.trans:
            self.trans.close()

    # 发送命令
    def send_cmd(self,cmd,channel):
        cmd += '\r'
        p = re.compile(r'#')
        result = ''
        channel.send(cmd)
        while True:
            sleep(0.5)
            ret = channel.recv(65535)
            ret = ret.decode('utf-8')
            result += ret
            print(ret)
            if p.search(ret):
                break
        return result

    # 建立sftp连接
    def sfp_connect(self):
        self.sftp = paramiko.SFTPClient.from_transport(self.trans)
        return self.sftp

    # 下载单个文件
    def sftp_get(self, remotefile, localfile,sftp):
        sftp.get(remotefile, localfile)

    # 上传单个文件
    def sftp_put(self, remotefile, localfile,sftp):
        sftp.put(remotefile, localfile)

    # 获取远程目录所有文件
    def get_all_remote_files(self,remote_dir,sftp):
        all_files=[]
        if remote_dir[-1]=='/':
            remote_dir=remote_dir[0:-1]
        files = sftp.listdir_attr(remote_dir)
        for x in files:
            filename = remote_dir + '/' + x.filename
            if S_ISDIR(x.st_mode):
                all_files.extend(self.get_all_remote_files(filename,sftp))
            else:
                all_files.append(filename)
        return all_files

    # 下载
    def sftp_get_dir(self, remote_dir, local_dir,sftp):
        all_files = self.get_all_remote_files(remote_dir,sftp)
        for x in all_files:
            filename = x.split('/')[-1]
            local_filename = os.path.join(local_dir, filename)
            sftp.get(x, local_filename)

    # 获取本地指定目录及其子目录下的所有文件
    def get_all_files_in_local_dir(self, local_dir):
        all_files = list()
        files = os.listdir(local_dir)
        for x in files:
            filename = os.path.join(local_dir, x)
            if os.path.isdir(x):
                all_files.extend(self.get_all_files_in_local_dir(filename))
            else:
                all_files.append(filename)
        return all_files

    # 上传
    def sftp_put_dir(self, local_dir, remote_dir,sftp):
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]
        all_files = self.get_all_files_in_local_dir(local_dir)
        for x in all_files:
            filename = os.path.split(x)[-1]
            remote_filename = remote_dir + '/' + filename
            sftp.put(x, remote_filename)


if __name__ == '__main__':
    rc = RemoteConnect('192.168.1.120',22,'root','123456')
    chan = rc.ssh_connect()
    rc.send_cmd('cd /home', chan)
    rc.send_cmd('ll',chan)
    sf = rc.sfp_connect()
    rc.sftp_get('/home/test.txt', r'D:\newtest.txt',sf)
    rc.ssh_close()




