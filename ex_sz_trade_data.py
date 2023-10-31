import os
import re

import camelot
import pandas as pd
import requests

from config import RES_DIR_PATH, OUTPUT_DIR_PATH
from ex_sz_binary_trade_data import _load_pdf_pages, _find_start_end_page_index
from log import logger

FIRST_LINE_TITLE_FLAG_LIST = ['字段名称', '文件', '序号', '类别名称',
                              'OrdRejReas\n原因简称 \n具体含义 \non',
                              '域名', '字段', '委托类型', '序号  字段名']


def check_sz_ex_trade_data_interface_file():
    url = 'http://www.szse.cn/marketServices/technicalservice/interface/'
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5'
    }
    res = requests.get(url, headers=headers)
    res.encoding = "utf-8"
    html = res.text

    res = re.search(r"curTitle ='深圳证券交易所数据文件交换接口规范（Ver(.*)）\';", html)
    cur_version = res[1]

    if cur_version:
        pdf_file_name = re.search(
            r"var curHref = '\./(.*).pdf\';\s* //var curTitle = '深圳证券交易所数据文件交换接口规范",
            html)[1]
        pdf_file_url = f'{url}{pdf_file_name}.pdf'
        res = requests.get(pdf_file_url)
        pdf_file_path = os.path.sep.join([RES_DIR_PATH, f'{pdf_file_name}.pdf'])
        with open(pdf_file_path, 'wb') as f:
            f.write(res.content)
        output_file_path = os.path.sep.join([OUTPUT_DIR_PATH, '深圳证券交易所数据文件交换接口规范.xlsx'])
        extract_table_from_pdf(pdf_file_path, output_file_path)


def extract_table_from_pdf(input_file_path, output_file_path):
    pages = _load_pdf_pages(input_file_path)
    start_page_i, end_page_i = _find_start_end_page_index(pages)

    table_list = find_table_on_page(input_file_path, start_page_i, end_page_i)

    dump_table_to_excel(table_list, output_file_path)

    file_name = os.path.split(output_file_path)[1]
    logger.info(f'完成对文件: {file_name} -的提取')


def find_table_on_page(input_file_path, start_page_i, end_page_i):
    table_list = []
    cur_table = []
    for page_i in range(start_page_i, end_page_i + 1):
        tables = camelot.read_pdf(input_file_path, pages=f'{page_i}')
        if len(tables) == 0:
            continue
        for table in tables:
            table = table.data
            first_line = table[0]
            if not cur_table:
                cur_table.extend(table)
            else:
                if first_line[0] not in FIRST_LINE_TITLE_FLAG_LIST and first_line[1] not in FIRST_LINE_TITLE_FLAG_LIST:
                    cur_table.extend(table)
                else:
                    table_list.append(cur_table)
                    cur_table = []
                    cur_table.extend(table)

    return table_list


def dump_table_to_excel(table_list, output_file_path):
    writer = pd.ExcelWriter(output_file_path)

    count = 0
    for i, table in enumerate(table_list):
        try:
            new_table = []
            for line in table:
                new_line = [item.replace('\n', '').replace(' ', '') for item in line]
                new_table.append(new_line)
            table = new_table
            df = pd.DataFrame(table, index=None)
            df.to_excel(writer, sheet_name=f'{count + 1}', index=False)
        except Exception as e:
            print(e)
        count += 1
    writer.close()


if __name__ == '__main__':
    check_sz_ex_trade_data_interface_file()