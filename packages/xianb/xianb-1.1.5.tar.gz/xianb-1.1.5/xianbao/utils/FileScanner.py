
import os
from collections import deque


def catalog_deep_list(folder: str, layer: int = 0) -> []:
    """扫描根目录下的日期格式目录
     Args:
        :param folder: 扫描的根目录路径
        :param layer: 上往下扫描多少层

     Returns:
         日期格式的目录相对路径列表，格式: ['20250701', '20250815', ...]

     Raises:
         ValueError: 如果根目录不存在
     """
    if not os.path.exists(folder):
        raise ValueError(f"目录不存在: {folder}")
    if not os.path.isdir(folder):
        raise ValueError(f"路径不是目录: {folder}")

    directories = []
    sta = deque([folder])
    layer_sta = deque([0])

    while len(sta) > 0:
        directory = sta.pop()
        current_layer = layer_sta.pop()

        if current_layer == layer or os.path.isfile(directory):
            directories.append(directory)
        elif os.path.isdir(directory):
            directory_list = os.listdir(directory)
            [sta.append(str(os.path.join(directory, c))) for c in directory_list]
            [layer_sta.append(current_layer + 1) for _ in range(1, len(directory_list) + 1)]

    return directories

