import os, psutil
from rich import print
from rich.console import Console

from rich.table import Column, Table
console = Console()

def get_cpu_info(thresh=0.2):
    thresh *= 100
    cpu_count = psutil.cpu_count(logical=False)  #1代表单核CPU，2代表双核CPU  
    xc_count = psutil.cpu_count()                #线程数，如双核四线程
    cpu_percent = round((psutil.cpu_percent(1)), 2)  # cpu使用率
    cpu_percent_list = psutil.cpu_percent(percpu=True)
    cpu_free_num = 0
    for i in cpu_percent_list:
        if i <= thresh:
            cpu_free_num += 1
    cpu_info = (cpu_count, xc_count, cpu_percent, cpu_free_num)
    return cpu_info

def get_memory_info():
    memory = psutil.virtual_memory()
    total_nc = round(( float(memory.total) / 1024 / 1024 / 1024), 2)  # 总内存
    used_nc = round(( float(memory.used) / 1024 / 1024 / 1024), 2)  # 已用内存
    free_nc = round(( float(memory.free) / 1024 / 1024 / 1024), 2)  # 空闲内存
    percent_nc = round((float(memory.used) / float(memory.total) * 100), 2)  # 内存使用率

    men_info= (total_nc,used_nc,free_nc,percent_nc)
    return men_info

def judge_disk_type(input_path):
    result_str = os.popen('grep ^ /sys/block/*/queue/rotational').read()
    str_list = result_str.strip().split('\n')
    for now_str in str_list:
        # print(now_str)
        path, disk_type = now_str.split(':')
        path = path.split('/')[3]
        disk_type = False if disk_type == '1' else True
        if 'loop' not in path:
            # print(f'当前磁盘: {path} 是 {"固态" if disk_type else "机械"} 硬盘！')
            if path in input_path:
                return disk_type
            # print(f'未找到当前磁盘 {input_path}!')

def get_disk_info():
    list = psutil.disk_partitions() #磁盘列表
    ilen = len(list) #磁盘分区个数
    i = 0
    retlist1 = []
    retlist2 = []
    disk_info_list = []
    while i < ilen:
        diskinfo = psutil.disk_usage(list[i].mountpoint)

        
        total_disk = round((float(diskinfo.total)/1024/1024/1024),2) #总大小
        used_disk = round((float(diskinfo.used) / 1024 / 1024 / 1024), 2) #已用大小
        free_disk = round((float(diskinfo.free) / 1024 / 1024 / 1024), 2) #剩余大小
        percent_disk = diskinfo.percent
        disk_type = judge_disk_type(list[i].device)
        if total_disk > 240 and list[i].mountpoint != '/':
            # print(f'磁盘: {list[i].device}, 挂载点: {list[i].mountpoint}, 磁盘格式: {list[i].fstype}, 磁盘类型: {"固态" if disk_type else "机械"} 硬盘, 大小: {total_disk}G, 已用: {used_disk}G, 可用 {free_disk}G, 空闲 {percent_disk}%')
            retlist1=[list[i].device, list[i].mountpoint, list[i].fstype, disk_type, total_disk, used_disk, free_disk, percent_disk, diskinfo, list[i]]
            disk_info_list.append(retlist1)  
        i=i+1

    return disk_info_list




def show_disk_info(disk_list):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("磁盘", style="dim", width=12)
    table.add_column("挂载点")
    table.add_column("磁盘格式", justify="right")
    table.add_column("磁盘类型", justify="right")
    table.add_column("容量", justify="right")
    table.add_column("已用", justify="right")
    table.add_column("可用", justify="right")
    table.add_column("占用率", justify="right")
    for now_disk in disk_list:
        print(len(now_disk))
        table.add_row(now_disk[0], now_disk[1], now_disk[2], f'{"固态" if now_disk[3] else "机械"} 硬盘',
         f'{"%.2fTB"%(now_disk[4]/1024) if now_disk[4] > 1024 else "%.2fGB"%(now_disk[4])}',
         f'{"%.2fTB"%(now_disk[5]/1024) if now_disk[5] > 1024 else "%.2fGB"%(now_disk[5])}',
         f'{"%.2fTB"%(now_disk[6]/1024) if now_disk[6] > 1024 else "%.2fGB"%(now_disk[6])}',
         "%.2f%%"%(now_disk[7]))
    console.print(table)

def get_system_drives():
    drives = []
    for disk in psutil.disk_partitions(all=True):
        drive = disk.mountpoint
        # if is_windows():
        #     drive = os.path.splitdrive(drive)[0]
        drives.append(drive)
    drives.sort(reverse=True)
    return drives

if __name__ == '__main__':
    cpu = get_cpu_info()
    print(cpu)

    mem = get_memory_info()
    print(mem)




    disk_l = get_disk_info()
    # for disk in disk_l:
    #     print(disk)

    show_disk_info(disk_l)
    
