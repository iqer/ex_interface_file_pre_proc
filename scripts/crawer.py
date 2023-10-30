# import os
# import re
#
# import requests
#
# from log import logger
# from scripts.config import RES_DIR_PATH, OUTPUT_DIR_PATH
#
# FILE_NAME = '深圳证券交易所Binary交易数据接口规范（Ver1.29）.pdf'
# OUTPUT_EXCEL_FILE_NAME = '深圳证券交易所Binary交易数据接口规范（Ver1.29）.xlsx'
# FILE_PATH = os.path.sep.join([RES_DIR_PATH, FILE_NAME])
# OUTPUT_EXCEL_FILE_PATH = os.path.sep.join([OUTPUT_DIR_PATH, OUTPUT_EXCEL_FILE_NAME])
#
#
#
# def check_sz_ex_interface_file():
#     """获取深交所接口文件更新
#     """
#     url = 'http://www.szse.cn/marketServices/technicalservice/interface/'
#     res = requests.get(url)
#     res.encoding = "utf-8"
#     html = res.text
#
#     res = re.search(r"curTitle ='深圳证券交易所Binary交易数据接口规范（Ver(.*)）\';", html)
#     try:
#         cur_version = res[1]
#
#         if cur_version:
#             pdf_file_name = re.search(
#                 r"var curHref = '\./(.*).pdf\';\s* //var curTitle = '深圳证券交易所Binary交易数据接口规范",
#                 html)[1]
#             pdf_file_url = f'{url}{pdf_file_name}.pdf'
#             res = requests.get(pdf_file_url)
#             with open(FILE_PATH, 'wb') as f:
#                 f.write(res.content)
#             extract_table_from_pdf(FILE_PATH)
#             logger.info(f'深交所-接口文件-深圳证券交易所Binary交易数据接口规范: v{cur_version}')
#
#     except Exception:
#         import traceback
#         logger.warning(traceback.format_exc())
#
#
# if __name__ == '__main__':
#     check_sz_ex_interface_file()
