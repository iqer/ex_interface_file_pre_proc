"""
用于处理上交所易所撮合规范文件
"""
import os
import time

import camelot
import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import RES_DIR_PATH, OUTPUT_DIR_PATH
from ex_sz_binary_trade_data import _load_pdf_pages, _find_start_end_page_index
from log import logger

FIRST_LINE_TITLE_FLAG_LIST = [
    '序号', '序号  字段名', '序 号', '委托类型', '业务分类', '类型', '名称', 'ID', '字段号', '销售人', '返回代码'
]


def check_sh_ex_trade_data_interface_file():
    url_root = 'http://www.sse.com.cn'
    url = 'http://www.sse.com.cn/services/tradingtech/data/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5'
    }
    time.sleep(10)

    res = requests.get(url, headers=headers)
    res.encoding = "utf-8"
    html = res.text

    soup = BeautifulSoup(html, "html.parser")

    notice_item = soup.find("div", id="sse_list_1")
    a_list = notice_item.select("a")
    file_item = None
    for a in a_list:
        if 'IS101_上海证券交易所竞价撮合平台市场参与者接口规格说明书' in a.text:
            file_item = a
            break
    if not file_item:
        return

    pdf_file_url = f'{url_root}{file_item.attrs["href"]}'
    time.sleep(10)
    res = requests.get(pdf_file_url, headers=headers)
    pdf_file_path = os.path.sep.join([RES_DIR_PATH, f"{file_item.attrs['href'].split('/')[-1]}"])
    with open(pdf_file_path, 'wb') as f:
        f.write(res.content)
    output_file_path = os.path.sep.join(
        [OUTPUT_DIR_PATH, 'IS101_上海证券交易所竞价撮合平台市场参与者接口规格说明书.xlsx'])
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
            if '接口' in first_line[0] or '信息' in first_line[0] or 'txt' in first_line[0] or 'TXT' in first_line[0]:
                second_line = table[1]
                if second_line[0] in FIRST_LINE_TITLE_FLAG_LIST:
                    table = table[1:]
                    first_line = table[0]
                else:
                    continue
            if not cur_table:
                cur_table.extend(table)
                continue
            else:
                if first_line[0] in FIRST_LINE_TITLE_FLAG_LIST:
                    table_list.append(cur_table)
                    cur_table = []
                    cur_table.extend(table)
                    continue
                else:
                    cur_table.extend(table)
                    continue

    if cur_table:
        table_list.append(cur_table)

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
            logger.warning(e)
        count += 1
    writer.close()


if __name__ == '__main__':
    check_sh_ex_trade_data_interface_file()
