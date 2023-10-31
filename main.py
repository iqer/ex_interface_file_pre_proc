from multiprocessing import Process

from ex_sh_binary_trade_data import check_sh_ex_binary_trade_data_interface_file
from ex_sh_trade_interface import check_sh_ex_trade_data_interface_file
from ex_sz_binary_trade_data import check_sz_ex_binary_trade_interface_file
from ex_sz_trade_data import check_sz_ex_trade_data_interface_file

job_list = [
    check_sz_ex_binary_trade_interface_file,
    check_sz_ex_trade_data_interface_file,
    check_sh_ex_trade_data_interface_file,
    check_sh_ex_binary_trade_data_interface_file,
]


def main():
    p_list = []

    for job in job_list:
        p = Process(target=job)
        p.start()
        p_list.append(p)

    for p in p_list:
        p.join()


if __name__ == '__main__':
    main()
