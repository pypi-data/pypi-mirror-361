# coding=utf-8
from xtquant import xtdata

# 获取板块列表
sector_name_df = xtdata.get_sector_list()
# 根据板块列表找查询指数索引名称
sector_name_index = xtdata.get_stock_list_in_sector('上证A股')

print(sector_name_index)