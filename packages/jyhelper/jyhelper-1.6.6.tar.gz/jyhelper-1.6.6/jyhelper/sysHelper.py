#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time : 2025/01/13 18:35 
# @Author : JY
"""
系统相关的操作
"""

import subprocess
import sys
import json
import locale
import time


class sysHelper:

    @staticmethod
    def run_command(command, printInfo=True, returnStr=False, returnJson=False,encoding_utf8=False,encoding_gbk=False,timeout=None):
        """
        :param command: 执行的命令
        :param printInfo: 是否打印info信息
        :param returnStr: 返回字符串 默认返回list
        :param returnJson: 返回json解析后的python可直接操作对象
        :param encoding_utf8:
        :param encoding_gbk:
        :param timeout: 超时时间 默认None不超时，可以设定一个秒数
        :return: 默认list 可选字符串和json解析后的对象
        """
        res_lines = []
        encoding = locale.getpreferredencoding(False)
        if encoding_utf8:
            encoding = 'utf-8'
        if encoding_gbk:
            encoding = 'gbk'
        if printInfo:
            print('info','run:',command)
        start_time = time.time()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                   text=True,encoding=encoding)  # stderr=subprocess.PIPE,可以捕获错误，不设置就是直接输出
        printRes = False
        while True:
            if timeout is not None and time.time() - start_time > timeout:
                process.kill()
                print(sysHelper.red('Error'),sysHelper.red(f"Max allow {timeout} seconds, Time out!"))
                return None

            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                outStr = output.strip()
                res_lines.append(outStr)
                if printInfo:
                    if not printRes:
                        print('info', 'res:')
                        printRes = True
                    print(outStr)
                sys.stdout.flush()
        
        if returnStr:
            res_lines = '\n'.join(res_lines)
        if returnJson:
            res_lines = ''.join(res_lines)
            res_lines = json.loads(res_lines)
        exit_code = process.poll()
        if exit_code != 0:
            print(sysHelper.red('Error: '))
            for line in process.stderr:
                print(sysHelper.red(line.strip()))
            if isinstance(res_lines,list):
                for row in res_lines:
                    print(sysHelper.red(row))
            else:
                print(sysHelper.red(str(res_lines)))
            return None
        return res_lines

    @staticmethod
    def red(msg):
        """print以后会显示亮红色字体"""
        return f"\033[91m{msg}\033[0m"

    @staticmethod
    def green(msg):
        """print以后会显示亮绿色字体"""
        return f"\033[92m{msg}\033[0m"

    @staticmethod
    def display_all_colors():
        """
        显示全部可用的颜色
        :return:
        """
        j = 0
        for i in range(108):
            if i in [2, 3, 5, 6, 8, 38, 39, 48, 49, 50, 98] or 10 <= i <= 20 or 22 <= i <= 29 or 52 <= i <= 89:
                continue
            msg = f"\033[{i}m" + r"\033[%sm内容\033[0m" % i + "\033[0m"
            if i < 10:
                msg += " "
            if i < 100:
                msg += " "
            print(msg, '', '', end='')
            j += 1
            if j % 8 == 0:
                print()

    @staticmethod
    def logError(msg1='', msg2='', msg3=''):
        """1个参数默认就是红色，2个或者3个参数msg2是红色"""
        if msg2 == '' and msg3 == '':
            print(sysHelper.red(msg1))
        elif msg2 != '' and msg3 == '':
            print(msg1, sysHelper.red(msg2))
        elif msg2 != '' and msg3 != '':
            print(msg1, sysHelper.red(msg2), msg3)

    @staticmethod
    def logInfo(msg1='', msg2='', msg3=''):
        if msg2 == '' and msg3 == '':
            print(sysHelper.green(msg1))
        elif msg2 != '' and msg3 == '':
            print(msg1, sysHelper.green(msg2))
        elif msg2 != '' and msg3 != '':
            print(msg1, sysHelper.green(msg2), msg3)


if __name__ == '__main__':
    cmd = 'ping www.abaidu.com'
    res = sysHelper.run_command(cmd,returnStr=True)
    print('--------返回的结果---------')
    print(res)
