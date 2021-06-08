from utils.hard_core import *
from rich import print
from rich.align import Align

from rich.console import Console
from rich.table import Column, Table
import os, psutil, subprocess, shutil, time, datetime
console = Console()

def count_time_format(minuate):
    if isinstance(minuate, str):
        return minuate
    return time.strftime("%H:%M:%S", time.gmtime(minuate))

def time_format(timestep):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestep))

class DISK(object):
    def __init__(self, disk_part):
        # print(disk_part)
        self.mountpoint = disk_part.mountpoint
        self.device = disk_part.device
        self.disk_info = psutil.disk_usage(self.mountpoint)
        self.total_disk = round((float(self.disk_info.total) / 1024 / 1024 / 1024), 2) #总大小
        self.used_disk = round((float(self.disk_info.used) / 1024 / 1024 / 1024), 2) #已用大小
        self.free_disk = round((float(self.disk_info.free) / 1024 / 1024 / 1024), 2) #剩余大小
        self.percent_disk = self.disk_info.percent
        self.disk_type = judge_disk_type(self.device)
        self.occupy_list = []
        self.get_max_plot_size()
        # self.show_disk_info()
        
        
    def get_free_size(self):
        self.free_disk = round((float(psutil.disk_usage(self.mountpoint).free) / 1024 / 1024 / 1024), 2)
        return self.free_disk
    
    def get_used_size(self):
        self.used_disk = round((float(psutil.disk_usage(self.mountpoint).used) / 1024 / 1024 / 1024), 2)
        return self.used_disk
    
    def get_total_size(self):
        return self.total_disk
    
    def get_percent(self):
        return self.disk_info.percent
    
    def get_max_plot_size(self, k=32):
        assert k==32, print(u'暂时只支持k32!')
        single_plot_size = 239
        free_size = self.get_free_size()
        self.max_plot_size = free_size // single_plot_size
        self.max_plot_size -= len(self.occupy_list)
        # print(f'当前磁盘: {self.mountpoint}, 已用 {self.get_used_size()}G. 剩余{self.free_disk}G. 可P K32个数 : {self.max_plot_size}')
        return self.max_plot_size
    
    def get_max_farm_size(self, k=32):
        assert k==32, print(u'暂时只支持k32!')
        single_farm_size = 102
        free_size = self.get_free_size()
        self.max_farm_size = free_size // single_farm_size
        self.max_farm_size -= len(self.occupy_list)
        # print(f'当前磁盘: {self.mountpoint}, 已用 {self.get_used_size()}G. 剩余{self.free_disk}G. 可P K32个数 : {self.max_plot_size}')
        return self.max_farm_size

    def show_disk_info(self):

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("磁盘", style="dim", width=12)
        table.add_column("挂载点")
        table.add_column("磁盘类型", justify="right")
        table.add_column("容量", justify="right")
        table.add_column("已用", justify="right")
        table.add_column("可用", justify="right")
        table.add_column("占用率", justify="right")
        table.add_column("计划已占用P盘个数", justify="right")
        save_num = 0
        if self.disk_type:
            table.add_column("剩余可P K32个数", justify="right")
            save_num = str(self.get_max_plot_size())
        else:
            table.add_column("剩余可存K32文件个数", justify="right")
            save_num = str(self.get_max_farm_size())
        self.get_used_size()
        self.get_percent()
        # self.get_max_plot_size()
        table.add_row(self.device, self.mountpoint, f'{"固态" if self.disk_type else "机械"} 硬盘',
        f'{"%.2fTB"%(self.total_disk/1024) if self.total_disk > 1024 else "%.2fGB"%(self.total_disk)}',
        f'{"%.2fTB"%(self.used_disk/1024) if self.used_disk > 1024 else "%.2fGB"%(self.used_disk)}',
        f'{"%.2fTB"%(self.free_disk/1024) if self.free_disk > 1024 else "%.2fGB"%(self.free_disk)}',
        "%.2f%%"%(self.percent_disk), str(len(self.occupy_list)), save_num)
        console.print(table)

class CPUManager(object):
    # CPU管理者 获取CPU型号、核心数、线程数、占用率， 以及管理P盘时CPU调度
    def __init__(self, max_thread_num=None):
        self.cpu_info = get_cpu_info()
        self.core_num = self.cpu_info[0]
        self.thread_num = self.cpu_info[1]
        self.used_num = 0
        if max_thread_num is not None:
            self.max_thread_num = max_thread_num
        else:
            self.max_thread_num = int(0.75 * self.thread_num)
        self.free_cpu_list = [i for i in range(self.max_thread_num)]
    
    def set_cpu_occupy(self, plot_worker):
        self.used_num += plot_worker.thread_number
        self.used_num = min(self.max_thread_num, self.used_num)
        plot_worker.cpu_list = self.free_cpu_list[:plot_worker.thread_number]
        self.free_cpu_list = self.free_cpu_list[plot_worker.thread_number:]

    
    def get_cpu_free_num(self):
        # self.cpu_info = get_cpu_info()
        now_free_num = self.max_thread_num - self.used_num
        return now_free_num


    def set_cpu_free(self, plot_worker):
        if plot_worker.finish or plot_worker.logger.get_percent_step()[1] == 4:
            self.used_num -= plot_worker.thread_number
            self.used_num = max(self.used_num, 0)
            self.free_cpu_list += plot_worker.cpu_list
            plot_worker.cpu_list = []
            print(f'清除任务{plot_worker.name}的CPU占用！目前可用CPU为 {self.free_cpu_list}')

        # elif plot_worker.logger.get_percent_step()[1] != 1:
        #     self.used_num -= plot_worker.thread_number - 1
        #     self.used_num = max(self.used_num, 0)
    
    def view_info(self):
        print(f'当前CPU核心数: {self.thread_num},最大可用数量: {self.max_thread_num},已使用数量: {self.used_num}')

class SSDManager(object):
    # 固态硬盘管理者 获取固态硬盘列表，每块SSD的大小，占用率，以及管理P盘时SSD调度
    def __init__(self, ssd_path_list=None):
        self.auto_get_ssd_list(ssd_path_list)
        self.disk_dict = {}
        
        for now_path in self.ssd_list:
            self.disk_dict[now_path.mountpoint] = DISK(now_path)

    def auto_get_ssd_list(self, ssd_path_list=None, min_size=240):
        self.ssd_list = []
        disk_list = get_disk_info()
        for now_disk in disk_list:
            # print(now_disk)
            if now_disk[3]:
                if ssd_path_list is None:
                    self.ssd_list.append(now_disk[-1])
                elif ssd_path_list is not None and now_disk[0] in ssd_path_list:
                    self.ssd_list.append(now_disk[-1])

    def set_ssd_occupy(self, worker_name):
        max_internal_time = 0
        out_path = ''
        for path, disk in self.disk_dict.items():
            max_num = disk.get_max_plot_size()
            if max_num > 0:
                if disk.occupy_list == []:
                    out_path = path
                    break
                else:
                    now_internal_time = time.time() - disk.occupy_list[-1][-1]
                    if now_internal_time > max_internal_time:
                        max_internal_time = now_internal_time
                        out_path = path
        if not out_path:
            print(u'[red]SSD的P盘空间不足！')
        else:
            print(out_path, worker_name)
            self.disk_dict[out_path].occupy_list.append([worker_name, time.time()])
            out_path = out_path + f'/{worker_name}/'
            if os.path.exists(out_path):
                print(f'[red]路径{out_path}已存在 删除并重新创建！')
                shutil.rmtree(out_path)
            
            os.makedirs(out_path)

        return out_path
    
    def set_ssd_free(self, worker_name):
        for path, disk in self.disk_dict.items():
            for l in disk.occupy_list:
                if l[0] == worker_name:
                    disk.occupy_list.remove(l)
                    print(f'{worker_name} 完成! 缓存队列占用清除 {path} ')
                    return True
        print(f'未找到 {worker_name} 占用的缓存队列 ')
        return False

    def get_ssd_occupy(self, disk_name):
        assert disk_name in self.disk_dict, print(f'{disk_name} 不在 {self.disk_dict.keys()}中！')
        return self.disk_dict[disk_name].occupy_list

    def get_ssd_max_plot_number(self, disk_path, k=32):
        assert k==32, print(u'暂时只支持k32!')
        assert disk_path in self.disk_dict, print(f'{disk_path} 没有出现在 {self.disk_dict} 中！')
        return self.disk_dict[disk_path].get_max_plot_size()
    
    def get_all_max_plot_number(self, k=32):
        n = 0
        for k, v in self.disk_dict.items():
            n += v.get_max_plot_size()
        return n
    
    def get_total_ssd_status(self):
        used, free, total = 0, 0, 0
        for path, disk in self.disk_dict.items():
            used += disk.get_used_size()
            free += disk.get_free_size()
            total += disk.get_total_size()
        return used, free, total

    def view_info_table(self):
        table = Table(show_header=True, header_style="bold magenta")
        table_centered = Align.center(table)
        table.title = "SSD情况概览"
        table.add_column("磁盘", style="dim", width=12)
        table.add_column("挂载点")
        table.add_column("磁盘类型", justify="right")
        table.add_column("容量", justify="right")
        table.add_column("已用", justify="right")
        table.add_column("可用", justify="right")
        table.add_column("占用率", justify="right")
        table.add_column("已占P盘个数", justify="right")
        table.add_column("剩余可P K32", justify="right")
        for path, disk in self.disk_dict.items():
            save_num = str(disk.get_max_plot_size())
            disk.get_used_size()
            disk.get_percent()
            disk.get_max_plot_size()
            table.add_row(disk.device, disk.mountpoint, f'{"固态" if disk.disk_type else "机械"} 硬盘',
            f'{"%.2fTB"%(disk.total_disk/1024) if disk.total_disk > 1024 else "%.2fGB"%(disk.total_disk)}',
            f'{"%.2fTB"%(disk.used_disk/1024) if disk.used_disk > 1024 else "%.2fGB"%(disk.used_disk)}',
            f'{"%.2fTB"%(disk.free_disk/1024) if disk.free_disk > 1024 else "%.2fGB"%(disk.free_disk)}',
            "%.2f%%"%(disk.percent_disk), str(len(disk.occupy_list)), save_num)
        # console.print(table)
        return table

class HDDManager(object):
    # 机械硬盘管理者 获取机械硬盘列表，每块HDD的大小，占用率，以及管理P盘时输出路径调度
    def __init__(self, hdd_path_list=None):
        self.auto_get_hdd_list(hdd_path_list)
        self.disk_dict = {}
        
        for now_path in self.hdd_list:
            self.disk_dict[now_path.mountpoint] = DISK(now_path)

    def auto_get_hdd_list(self, hdd_path_list=None):
        self.hdd_list = []
        disk_list = get_disk_info()
        for now_disk in disk_list:
            if not now_disk[3]:
                if hdd_path_list is None:
                    self.hdd_list.append(now_disk[-1])
                elif hdd_path_list is not None and now_disk[0] in hdd_path_list:
                    self.hdd_list.append(now_disk[-1])

    def set_hdd_occupy(self, worker_name, delay_minute):
        delay_minute *= 60
        max_internal_time = 0
        out_path = ''
        for path, disk in self.disk_dict.items():
            max_num = disk.get_max_farm_size()
            if max_num > 0:
                if disk.occupy_list == []:
                    out_path = path
                    break
                else:
                    now_internal_time = time.time() - disk.occupy_list[-1][-1]
                    # 寻找距离上次任务间隔时间最长的机械盘写入，使机械盘IO利用率最大 
                    if now_internal_time > max_internal_time and now_internal_time >= delay_minute:
                        max_internal_time = now_internal_time
                        out_path = path
        if not out_path:
            if max_internal_time < delay_minute:
                pass
                # print(f'[red]当前机械盘执行任务距离上次任务时间间隔 {max_internal_time}分钟 小于 {delay_minute//60}分钟! 无法继续申请，等待{delay_minute//60 - max_internal_time}分钟后再尝试')
            else:
                print(u'[red]P盘空间不足！')
        else:
            self.disk_dict[out_path].occupy_list.append([worker_name, time.time()])

        return out_path
    
    def get_hdd_max_plot_number(self, disk_path, k=32):
        assert k==32, print(u'暂时只支持k32!')
        assert disk_path in self.disk_dict, print(f'{disk_path} 没有出现在 {self.disk_dict} 中！')
        return self.disk_dict[disk_path].get_max_farm_size()

    def get_all_max_plot_number(self, k=32):
        n = 0
        for k, v in self.disk_dict.items():
            n += v.get_max_farm_size()
        return n

    def get_total_hdd_status(self):
        used, free, total = 0, 0, 0
        for path, disk in self.disk_dict.items():
            used += disk.get_used_size()
            free += disk.get_free_size()
            total += disk.get_total_size()
        return used, free, total

    def view_info_table(self):
        table = Table(show_header=True, header_style="bold magenta")
        table_centered = Align.center(table)
        table.title = "HDD情况概览"
        table.add_column("磁盘", style="dim", width=12)
        table.add_column("挂载点")
        table.add_column("磁盘类型", justify="right")
        table.add_column("容量", justify="right")
        table.add_column("已用", justify="right")
        table.add_column("可用", justify="right")
        table.add_column("占用率", justify="right")
        table.add_column("已占K32数", justify="right")
        table.add_column("可存K32数", justify="right")
        for path, disk in self.disk_dict.items():
            save_num = str(disk.get_max_farm_size())
            disk.get_used_size()
            disk.get_percent()
            table.add_row(disk.device, disk.mountpoint, f'{"固态" if disk.disk_type else "机械"} 硬盘',
            f'{"%.2fTB"%(disk.total_disk/1024) if disk.total_disk > 1024 else "%.2fGB"%(disk.total_disk)}',
            f'{"%.2fTB"%(disk.used_disk/1024) if disk.used_disk > 1024 else "%.2fGB"%(disk.used_disk)}',
            f'{"%.2fTB"%(disk.free_disk/1024) if disk.free_disk > 1024 else "%.2fGB"%(disk.free_disk)}',
            "%.2f%%"%(disk.percent_disk), str(len(disk.occupy_list)), save_num)
        # console.print(table)
        return table

class LogProcesser(object):
    def __init__(self, log_file):
        self.end_1 = 799
        self.end_2 = 833
        self.end_3 = 2472
        self.end_4 = 2624
        self.len_1 = self.end_1
        self.len_2 = self.end_2 - self.end_1
        self.len_3 = self.end_3 - self.end_2
        self.len_4 = self.end_4 - self.end_3
        self.weight_1 = 0.44
        self.weight_2 = 0.163
        self.weight_3 = 0.35
        self.weight_4 = 0.047
        self.file_path = log_file
        self.start_time = time.time()
    
    def get_iter(self):
        l = []
        with open(self.file_path, 'r') as f:
            l = f.readlines()
        return len(l)

    def get_endurance_time(self):
        return time.time() - self.start_time

    def get_remaining_time(self, endurance_time, percent):

        remaining_time = '--:--:--' if percent < 0.01 else (endurance_time / percent) * (1 - percent)
        return remaining_time

    def get_percent_step(self):
        iter = self.get_iter()
        percent = 0.0
        step = 1
        if iter <= self.end_1:
            percent = self.weight_1 * (iter / self.len_1)
        elif iter > self.end_1 and iter <= self.end_2:
            percent = self.weight_2 * ((iter - self.end_1) / self.len_2) + self.weight_1
            step = 2
        elif iter > self.end_2 and iter <= self.end_3:
            percent = self.weight_3 * ((iter - self.end_2) / self.len_3) + self.weight_1 + self.weight_2
            step = 3
        elif iter > self.end_3 and iter <= self.end_4:
            percent = self.weight_4 * ((iter - self.end_3) / self.len_4) + self.weight_1 + self.weight_2 + self.weight_3
            step = 4
        return percent, step

class PlotWorker(object):
    # 每个plot程序的worker
    def __init__(self, id, cpu_man, config, plot_bpath, farm_bpath):
        self.id = id
        self.name = f'plot_{self.id}'
        self.plot_base_path = plot_bpath
        self.farm_base_path = farm_bpath
        self.k = config.k
        self.memory_occupy = config.memory
        self.cpu_list = []
        self.bucket = config.bucket
        self.start_time = time.time()
        self.thread_number = config.thread_number
        self.config = config
        cpu_man.set_cpu_occupy(self)
        self.log_file = config.log_path + f'plot_{self.id}.log'
        if not os.path.exists(config.log_path):
            os.makedirs(config.log_path)
        self.logger = LogProcesser(self.log_file)
        self.finish = False
    
    def get_status(self):
        percent, step = self.logger.get_percent_step()
        return percent, step

    def get_info(self):
        endurance_time = self.logger.get_endurance_time()
        percent, step = self.get_status()
        iter = self.logger.get_iter()
        endurance_time_str = count_time_format(endurance_time)
        remaining_time_str = count_time_format(self.logger.get_remaining_time(endurance_time, percent))
        # 任务名，pid，占用的cpu核心， 百分比, iter, 开始时间，持续时间，未来用时，目前阶段，plot缓存路径，输出路径
        info_list = [self.name, str(self.pid), ', '.join([str(i) for i in self.cpu_list]), percent, str(iter), f'{step} / 4', time_format(self.start_time), endurance_time_str, remaining_time_str,self.plot_base_path, self.farm_base_path]
        return info_list

    def do_work(self, config):
        
        # assert os.path.exists(self.plot_base_path) and os.path.exists(self.farm_base_path), print(f'plot路径{self.plot_base_path} 或 输出路径 {self.farm_base_path} 不存在!')
        self.start_time = time.time()
        log = open(self.log_file, 'w')
        args = [self.config.chia_exec, 'plots', 'create', '-k', str(self.k), '-n', '1', '-r', str(self.thread_number), '-u', str(self.bucket), '-b', str(int(self.memory_occupy)), '-t', self.plot_base_path, '-d', self.farm_base_path]
        # print(args)
        process = subprocess.Popen(
            args=args,
            stdout=log,
            stderr=log,
            shell=False,
        )
        self.process = process
        self.pid = process.pid
        psutil.Process(self.pid).cpu_affinity(self.cpu_list)
        print(f'添加新任务 {self.name}! 添加时间: {time_format(self.start_time)} 缓存位置: {self.plot_base_path}, 输出位置: {self.farm_base_path}, 占用CPU为 {self.cpu_list}, pid: {self.pid}')
        return process
    
    def finish_work(self, ssd_man, cpu_man):
        time.sleep(1)
        print(f'调用任务{self.name} finish! {self.plot_base_path}')
        self.finish = True 
        assert len(os.listdir(self.plot_base_path)) == 0, print(f'{self.plot_base_path} 文件夹非空! 完成任务 {self.name} 失败!')
        assert subprocess.Popen.poll(self.process) is not None, print(f'{self.name} 任务未完成')
        shutil.rmtree(self.plot_base_path)
        ssd_man.set_ssd_free(self.name)
        if self.cpu_list:
            cpu_man.set_cpu_free(self)


    def view_info(self):
        pass

class MemManager(object):
    def __init__(self):
        self.mem = psutil.virtual_memory()
        self.max_memory = self.mem.total / 1024 / 1024 / 1024
        self.free_memory = self.get_free_memory()
        self.used_memory = self.get_used_memory()
        self.percent = self.get_mem_percent()
    
    def get_free_memory(self):
        self.free_memory = psutil.virtual_memory().available / 1024 / 1024 / 1024
        return self.free_memory

    def get_used_memory(self):
        self.used_memory = self.max_memory - psutil.virtual_memory().available / 1024 / 1024 / 1024
        return self.used_memory

    def get_mem_percent(self):
        self.percent = self.get_used_memory() / self.max_memory
        return self.percent
    
    def get_max_alloc_num(self, plot_memory_size=4000.0):
        plot_memory_size /= 1024
        # print(self.free_memory, plot_memory_size)
        # print(int(self.free_memory / plot_memory_size))
        return int(self.free_memory / plot_memory_size)

    def view_info(self):
        print(f'内存使用情况: {self.get_used_memory() :.2f}GB/{self.max_memory :.2f}GB 空闲内存: {self.get_free_memory() :.2f}GB 利用率: {self.get_mem_percent() :.2f}%')

class Manager(object):
    def __init__(self, config):
        self._cpu = CPUManager()
        self._ssd = SSDManager()
        self._hdd = HDDManager()
        self._mem = MemManager()
        self.worker_queue = []
        self.now_worker_id = 0
        self.max_parallel_num = config.max_parallel_num
        self.config = config
        self.start_time = time.time()
        self.finish_time_list = []
    
    def get_running_worker_num(self):
        return len(self.worker_queue)
    
    def last_24h_finished_plot_number(self):
        if not self.finish_time_list:
            return 0
        now = time.time()
        one_day_ago = now - 86400
        for i in range(len(self.finish_time_list)):
            if self.finish_time_list[i] > one_day_ago:
                return len(self.finish_time_list[i:])
        return 0

    def get_max_allocable_worker_num(self):
        # 并行最大 - 正在跑的plot数量
        could_alloc_num = self.max_parallel_num - len(self.worker_queue)
        # CPU剩余可用核心数 / 每个任务占用核心数
        cpu_free_num = self._cpu.get_cpu_free_num() / self.config.thread_number
        # 内存剩余可P盘数
        mem_free_num = self._mem.get_max_alloc_num(self.config.memory)
        # 固态剩余可p盘数
        ssd_free_num = self._ssd.get_all_max_plot_number(self.config.k)
        # 储存盘剩余可p盘数
        hdd_free_num = self._hdd.get_all_max_plot_number(self.config.k)
        temp_n = 0
        for now_worker in self.worker_queue:
            p, step = now_worker.get_status()
            if step == 4:
                temp_n += 1
        # 可用跑第一阶段的剩余任务数量
        step_1_free_num = could_alloc_num + temp_n
        
        max_free_num = int(min(cpu_free_num, mem_free_num, ssd_free_num, hdd_free_num, step_1_free_num))
        max_free_num = max(0, max_free_num)
        return max_free_num

    def upgrade_worker_queue(self):
        all_working = False
        if not self.worker_queue:
            all_working = True
        while not all_working:
            for now_worker in self.worker_queue:
                if subprocess.Popen.poll(now_worker.process) is not None:
                    print(f'{now_worker.name} 任务完成！ 清除占用')
                    now_worker.finish_work(self._ssd, self._cpu)
                    self.finish_time_list.append(time.time())
                    # self._ssd.set_ssd_free(now_worker.name)
                    self.worker_queue.remove(now_worker)
                    break
                elif now_worker.get_status()[1] == 4 and now_worker.cpu_list:
                    self._cpu.set_cpu_free(now_worker)
            
            all_working = True
            for now_worker in self.worker_queue:
                if subprocess.Popen.poll(now_worker.process) is not None:
                    all_working = False
                    break
        
        n = self.get_max_allocable_worker_num()
        # print(f'当前资源至少可以再申请{n}个任务！')
        for i in range(n):
            success = self.new_worker(self.now_worker_id)
            if not success:
                # print(f'申请任务：{self.now_worker_id} 失败!')
                break
            self.now_worker_id += 1


    def new_worker(self, w_id):
        success = False
        worker_name = f'plot_{w_id}'
        interval_time = self.config.delay_minute
        farm_path = self._hdd.set_hdd_occupy(worker_name, interval_time)
        if farm_path:
            plot_path = self._ssd.set_ssd_occupy(worker_name)
            if plot_path:
                worker = PlotWorker(w_id, self._cpu, self.config, plot_path, farm_path)
                # print(w_id, plot_path, farm_path)
                # print(f'[red]!!!!!!!!!!!!!!!!!!!')
                worker.do_work(self.config)
                self.worker_queue.append(worker)
                success = True
            else:
                print(f'SSD磁盘空间不足 无法P更多文件 稍后再试') 
        else:
            # print(f'HDD磁盘空间不足 无法储存更多plot文件 稍后再试')
            pass
        
        return success

    def view_info(self):
        self._ssd.view_info()
        self._hdd.view_info()
        self._cpu.view_info()
        self._mem.view_info()
        





