import os, sys, psutil, subprocess
from plot_cfg import Config




if __name__ == '__main__':
    cfg = Config()
    now_id = 0
    if not os.path.exists(cfg.out_log_base_path):
        os.makedirs(cfg.out_log_base_path)
    
    assert len(cfg.plot_path_list) == len(cfg.out_path_list) and len(cfg.ssd_plot_number_list) == len(cfg.plot_path_list), u'plot 输入路径个数、plot number 个数与 output 输出路径个数必须一致'

    ln = len(cfg.plot_path_list)
    for i in range(ln):
        plot_path = cfg.plot_path_list[i]
        now_out_base_path = cfg.out_path_list[i]
        now_ssd_plot_number = cfg.ssd_plot_number_list[i]
        for j in range(now_ssd_plot_number):
            now_id += 1
            now_log_file = cfg.out_log_base_path + 'plot_log_%d.log'%(now_id)
            now_plot_path = plot_path + 'p%d/'%(now_id)
            if os.path.exists(now_plot_path):
                os.rmdir(now_plot_path)
                # pass
            os.makedirs(now_plot_path)
            # command = f'{cfg.chia_exec} plots create -k {cfg.k} -n {cfg.queue_size} -r {cfg.thread_n} -u {cfg.bucket_n} -b {cfg.memory} -t {now_plot_path} -d {now_out_base_path} > {now_log_file} &'
            command = f'{cfg.chia_exec} plots create -k {cfg.k} -n {cfg.queue_size} -r {cfg.thread_n} -u {cfg.bucket_n} -b {cfg.memory} -t {now_plot_path} -d {now_out_base_path}'

            print(command)
            # os.system(command)
            log_file = open(now_log_file, 'a')
            command_list = [cfg.chia_exec, 'plots', 'create', '-k', str(cfg.k), '-n', str(cfg.queue_size), '-r', str(cfg.thread_n), '-u', str(cfg.bucket_n), '-b', str(cfg.memory), '-t', now_plot_path, '-d', now_out_base_path]
            process = subprocess.Popen(args=command_list, stdout=log_file, stderr=log_file)
            psutil.Process(process.pid).cpu_affinity([i for i in range(cfg.thread_n)])
            print(process.pid)



    



