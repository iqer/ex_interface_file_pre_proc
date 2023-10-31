"""
用于处理文件名为深圳证券交易所Binary交易数据接口规范（VerNumber）.pdf的文件
"""
import os
import re
from collections import defaultdict

import camelot
import pandas as pd
import pdfplumber
import requests

from log import logger
from config import RES_DIR_PATH, OUTPUT_DIR_PATH

FIRST_TITLE_FLAG_LIST = ['Time', '域名', '应用标识 ApplID', '应用标识\nApplID',
                         '委托申报类型', '平台', '消息类型', '委托类型', '业务',
                         'MarketSegmentID', 'ApplID']

FILE_NAME = '深圳证券交易所Binary交易数据接口规范（Ver1.29）.pdf'
OUTPUT_EXCEL_FILE_NAME = '深圳证券交易所Binary交易数据接口规范（Ver1.29）.xlsx'
FILE_PATH = os.path.sep.join([RES_DIR_PATH, FILE_NAME])
OUTPUT_EXCEL_FILE_PATH = os.path.sep.join([OUTPUT_DIR_PATH, OUTPUT_EXCEL_FILE_NAME])


def check_sz_ex_interface_file():
    """获取深交所接口文件更新
    """
    url = 'http://www.szse.cn/marketServices/technicalservice/interface/'
    res = requests.get(url)
    res.encoding = "utf-8"
    html = res.text

    res = re.search(r"curTitle ='深圳证券交易所Binary交易数据接口规范（Ver(.*)）\';", html)
    try:
        cur_version = res[1]

        if cur_version:
            pdf_file_name = re.search(
                r"var curHref = '\./(.*).pdf\';\s* //var curTitle = '深圳证券交易所Binary交易数据接口规范",
                html)[1]
            pdf_file_url = f'{url}{pdf_file_name}.pdf'
            res = requests.get(pdf_file_url)
            with open(FILE_PATH, 'wb') as f:
                f.write(res.content)
            extract_table_from_pdf(FILE_PATH)

    except Exception:
        import traceback
        logger.warning(traceback.format_exc())


def extract_table_from_pdf(file_path):
    pages = _load_pdf_pages(file_path)
    start_page_i, end_page_i = _find_start_end_page_index(pages)
    page_title_data_map = find_table_on_page(start_page_i, end_page_i)
    dump_table_to_excel(page_title_data_map)
    logger.info(f'完成对文件: {FILE_NAME} -的提取')


def _load_pdf_pages(file_path):
    pdf = pdfplumber.open(file_path)
    pages = pdf.pages
    return pages


def dump_table_to_excel(page_title_data_map):
    writer = pd.ExcelWriter(OUTPUT_EXCEL_FILE_PATH)

    count = 0
    for i, tables in page_title_data_map.items():
        for t_i, table in enumerate(tables):
            try:
                new_table = []
                for line in table:
                    new_line = [item.replace('\n', '').replace(' ', '') for item in line]
                    new_table.append(new_line)
                table = new_table
                df = pd.DataFrame(table[1:], index=None, columns=table[0])
                to_excel_autowidth_and_border(writer, df, sheetname=f'{count + 1}', startrow=0, startcol=0)
            except Exception as e:
                df.to_excel(writer, sheet_name=f'{count + 1}', index=False)
            count += 1
    writer.close()


def to_excel_autowidth_and_border(writer, df, sheetname, startrow, startcol):
    df.to_excel(
        writer, sheet_name=sheetname, index=False, startrow=startrow, startcol=startcol
    )  # send df to writer
    workbook = writer.book
    worksheet = writer.sheets[sheetname]  # pull worksheet object
    formater = workbook.add_format({"border": 1})
    for idx, col in enumerate(df):  # loop through all columns
        series = df[col]
        max_len = (
                max(
                    (
                        series.astype(str).map(len).max(),  # len of largest item
                        # series.map(len).max(),
                        len(str(series.name)),  # len of column name/header
                    )
                )
                * 3
                + 1
        )  # adding a little extra space
        # print(max_len)
        worksheet.set_column(
            idx + startcol, idx + startcol, max_len
        )  # set column width
    first_row = startrow
    first_col = startcol
    last_row = startrow + len(df.index)
    last_col = startcol + len(df.columns)
    worksheet.conditional_format(
        first_row,
        first_col,
        last_row,
        last_col - 1,
        options={"type": "formula", "criteria": "True", "format": formater},
    )


def remove_arrow_table(table):
    new_table = []
    for line in table:
        new_line = [item for item in line if item not in ['→', '']]
        new_table.append(new_line)
    return new_table


def find_table_on_page(start_page_i, end_page_i):
    page_title_data_map = defaultdict(list)
    cur_table_start_page = None
    cur_table = []
    for page_i in range(start_page_i, end_page_i + 1):
        tables = camelot.read_pdf(FILE_PATH, pages=f'{page_i}')

        # 过滤读取的脏数据
        if len(tables) == 1 and tables[0].data == [[''], [''], [''], ['']]:
            continue

        if len(tables) == 1 and not cur_table:
            cur_table_start_page = page_i
            table = tables[0].data
            cur_table.extend(table)
            continue
        if len(tables) == 1 and cur_table:
            table = tables[0].data
            first_line = table[0]
            first_title = first_line[0]
            if first_title not in FIRST_TITLE_FLAG_LIST:
                cur_table.extend(table)
                continue
            else:
                # 保存到目前为止遍历到的表格
                page_title_data_map[cur_table_start_page].append(cur_table)
                # 清空列表, 重新开始缓存下一个表格的数据
                cur_table = []
                cur_table.extend(table)
                cur_table_start_page = page_i
                continue
        # 当前页的表格数量不止一个的情况下
        if len(tables) > 1 and not cur_table:
            for tb_i in range(len(tables)):
                if tb_i != len(tables) - 1:
                    table = tables[tb_i].data
                    cur_table.extend(table)
                    cur_table_start_page = page_i
                    page_title_data_map[cur_table_start_page].append(cur_table)
                    cur_table = []
                    continue
                else:
                    table = tables[tb_i].data
                    cur_table.extend(table)
                    continue
        if len(tables) > 1 and cur_table:
            for tb_i in range(len(tables)):
                if tb_i == 0:
                    table = tables[tb_i].data
                    first_line = table[0]
                    first_title = first_line[0]
                    if first_title not in FIRST_TITLE_FLAG_LIST:
                        cur_table.extend(table)
                        page_title_data_map[cur_table_start_page].append(cur_table)
                        cur_table = []
                        continue
                    else:
                        # 保存到目前为止遍历到的表格
                        page_title_data_map[cur_table_start_page].append(cur_table)
                        # 清空列表, 重新开始缓存下一个表格的数据
                        cur_table = []
                        cur_table.extend(table)
                        cur_table_start_page = page_i
                        page_title_data_map[cur_table_start_page].append(cur_table)
                        cur_table = []
                        continue
                elif tb_i < len(tables) - 1:
                    table = tables[tb_i].data
                    cur_table.extend(table)
                    cur_table_start_page = page_i
                    page_title_data_map[cur_table_start_page].append(cur_table)
                    cur_table = []
                    continue
                else:
                    table = tables[tb_i].data
                    cur_table.extend(table)
                    continue

    return page_title_data_map


def _find_start_end_page_index(pages):
    start_page_i = 1
    end_page_i = len(pages)
    for i, page in enumerate(pages):
        text = page.extract_text()
        if '前言' in text:
            start_page_i = i + 1
            break
    return start_page_i, end_page_i


if __name__ == '__main__':
    # extract_table_from_pdf(FILE_PATH)
    check_sz_ex_interface_file()