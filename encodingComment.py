#!/usr/bin/python2.7
# -*- coding:utf-8 -*-
import sys
import os
import re
import optparse

#行类型
EXEC_LINE = 1 #shell行
CODING_LINE = 2 #编码行
OTHER_LINE = 0 #其他行
#正则表达式
CODING_LINE_RE = "^#.*coding[:=]\s*[0-9A-Za-z-_.]+.*$"
CODING_RE = '\s*coding[:=]\s*[0-9A-Za-z-_.]+'
CODING = "# -*- coding:charset -*-\n"
VERSION = "0.0.2"

#全局变量
_file_name = "" #当前文件名
_verbose = False

codingline_rex = re.compile(CODING_LINE_RE)
coding_rex = re.compile(CODING_RE)


#判断文件后缀
def check_suffix(name, suffix, check = True):
    if check:
        if not os.path.exists(name):
            return False
    if name.strip().endswith(suffix):
        return True
    else:
        return False

#提取编码
def get_coding(line):
    if get_line_type(line) != CODING_LINE:
        return None
    else:
        coding = coding_rex.findall(line)
        return coding[0]

#获取行类型,返回：EXEC_LINE = 1 CODING_LINE = 2 OTHER_LINE = 0
def get_line_type(line):
    if line.strip().startswith('#!'):
        return EXEC_LINE
    elif len(codingline_rex.findall(line.strip())) > 0:
        return CODING_LINE
    else:
        return OTHER_LINE

#获取状态文件中前两行的状态信息，返回一个元组
def get_lines_type(lines):
    #逐行分析，只关心前两行
    length = len(lines)
    if length == 0: #空文本
        return (OTHER_LINE, OTHER_LINE)
    elif length == 1: #只有一行的情况
        return (get_line_type(lines[0]), OTHER_LINE)
    else: #超过一行，则只处理前两行
        return (get_line_type(lines[0]), get_line_type(lines[1]))


#处理文件
def process_file(name,charset = 'utf-8'):
    #先判断是否是py文件
    py_file = None
    lines  = None
    lines_type = None
    #using global vars
    global _file_name
    global _verbose
    _file_name = name

    if check_suffix(name,".py"):
        #verbose
        if _verbose:
            print ""
            print "processing:" + _file_name ,

        #打开文件,读入所有的行
        py_file = open(name, "r")
        try:
            lines = py_file.readlines()
            #读取状态
            lines_type = get_lines_type(lines)
        finally:
            #关闭文件
            py_file.close()
            
        #根据行的状态决定要插入的位置
        if cmp(lines_type, (OTHER_LINE, OTHER_LINE)) == 0:
            #首行既不是命令行声明也不是编码声明的情况
            #将编码声明加入首行
            lines.insert(0, CODING.replace("charset",charset))

            if _verbose:
                print "insert:" + charset

        elif cmp(lines_type,(EXEC_LINE, OTHER_LINE)) == 0:
            #首行是命令行声明，第二行非编码声明的情况,插入第二行
            lines.insert(1, CODING.replace("charset",charset))

            if _verbose:
                print "insert:" + charset

        elif cmp(lines_type, (EXEC_LINE, CODING_LINE)) == 0:
            
            if _verbose:
                #print codingRex.findall(lines[1])
                print "detected:" + get_coding(lines[1])
                return

        else:
            
            if _verbose:
                print "detected:" + get_coding(lines[0])
                return

        py_file = open(name, "w")
        try:
            py_file.writelines(lines)
        finally:
            py_file.close()

#处理目录(递归)
def process(path, depth = -1, charset = "utf-8"):
    #含递归深度控制
    #获取当前文件列表
    lists = os.listdir(path)
    for f in lists:
        tmp = os.path.join(path, f)
        #深度指定为负数时为无限递归
        if depth < 0:
            if os.path.isdir(tmp):
                process(tmp, depth, charset)
            else:
                process_file(tmp, charset)
        elif depth == 0: #当深度为零时，说明到达了递归深度，直接返回
            return
        else: #深度大于零继续递归，直到深度小于零或者循环
            if os.path.isdir(tmp):
                process(tmp, depth - 1, charset) #深度需要递减
            else:
                process_file(tmp, charset)


#主函数
def main():
    global _verbose
    #设置命令行分析器
    parser = optparse.OptionParser("%prog [-r|-d|-c |-v |-h] <file(s)|dir>\nthis small tool let you batching the coding comment under python2.x,to set the charset like 'utf-8'")
    parser.add_option("-r",  action="store_true", dest = "recursion", help = "recursively deal with the files and dirs", default = False)
    parser.add_option("-d", "--depth", type = "int", dest = "depth", help = "specify the recursion depth, it works with -r", default = -1)
    parser.add_option("-c", "--coding", dest = "coding" ,help = "specify the coding charset", default = "utf-8")
    parser.add_option("-v", action = "store_true", dest = "verbose" , help = "show the details of processing", default = False)
    #获取命令行参数
    opts , args = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
    if opts.verbose == True:
        _verbose = True

    if opts.recursion == True:
        if len(args) < 1:
            print "Your need specify one dir as an arg when using -r option"
            return -1
        if not os.path.isdir(args[0]):
            print "Your need specify one dir as an arg when using -r option"
            return -1
        process(args[0], opts.depth, opts.coding)
    else:
        #handle file(s)
        for arg in args:
            process_file(arg, opts.coding)




if __name__ == "__main__":
    main()
