import os
import shutil
from pathlib import Path
import numpy as np
from rasterio import open as rasterio_open
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def calculate_non_zero_ratio(tif_path):
    """
    计算tif影像中非(0,0,0)像素的占比

    参数:
    tif_path: tif文件路径

    返回:
    (文件路径, 非零像素占比)
    """
    try:
        with rasterio_open(tif_path) as src:
            # 读取所有波段
            img = src.read()

            # 确保是RGB图像
            if img.shape[0] != 3:
                print(f"警告: {tif_path} 不是3波段图像")
                return (tif_path, 0.0)

            # 转置为(height, width, channels)格式
            img = np.transpose(img, (1, 2, 0))

            # 计算非(0,0,0)像素的数量
            non_zero_pixels = np.any(img != 0, axis=2).sum()
            total_pixels = img.shape[0] * img.shape[1]

            ratio = non_zero_pixels / total_pixels
            return (tif_path, ratio)
    except Exception as e:
        print(f"处理 {tif_path} 时发生错误: {str(e)}")
        return (tif_path, 0.0)


def find_tif_files(root_dir):
    """
    递归查找所有tif文件
    """
    tif_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.tif'):
                tif_files.append(os.path.join(root, file))
    return tif_files


def process_tif_directory(input_dir, output_dir, num_files=300, num_workers=4):
    """
    主处理函数

    参数:
    input_dir: 输入文件夹路径
    output_dir: 输出文件夹路径
    num_files: 需要选取的文件数量
    num_workers: 并行处理的线程数
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 查找所有tif文件
    print("正在搜索tif文件...")
    tif_files = find_tif_files(input_dir)
    total_files = len(tif_files)
    print(f"找到 {total_files} 个tif文件")

    if total_files == 0:
        print("未找到tif文件")
        return

    # 并行计算非零像素占比
    print("正在计算非零像素占比...")
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(
            executor.map(calculate_non_zero_ratio, tif_files),
            total=total_files,
            desc="处理进度"
        ))

    # 排序并选取前N个文件
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    selected_files = sorted_results[:min(num_files, total_files)]

    # 复制文件到新目录
    print(f"\n正在复制top {num_files} 文件到输出目录...")
    for file_path, ratio in tqdm(selected_files, desc="复制进度"):
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(output_dir, file_name)
        shutil.copy2(file_path, dest_path)

    print(f"\n处理完成！已将 {len(selected_files)} 个文件复制到 {output_dir}")

    # 输出统计信息
    print("\n统计信息:")
    print(f"处理的文件总数: {total_files}")
    print(f"选取的文件数量: {len(selected_files)}")
    print(f"最高非零像素占比: {selected_files[0][1]:.2%}")
    print(f"最低非零像素占比: {selected_files[-1][1]:.2%}")


if __name__ == "__main__":
    # 使用示例
    input_directory = r"F:\data\人居数据\01建成区+临桂区"  # 替换为你的输入目录
    output_directory = r"F:\data\人居数据\01建成区+临桂区\output"  # 替换为你的输出目录

    process_tif_directory(
        input_dir=input_directory,
        output_dir=output_directory,
        num_files=300,  # 选取前300个文件
        num_workers=4  # 使用4个线程并行处理
    )