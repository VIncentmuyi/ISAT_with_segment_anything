from PIL import Image
import os


def convert_tif_to_png(input_folder, output_folder):
    # 如果输出文件夹不存在，创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 检查文件是否是tif格式
        if filename.lower().endswith(('.tif', '.tiff')):
            # 构建完整的输入文件路径
            input_path = os.path.join(input_folder, filename)

            # 构建输出文件路径，将扩展名改为.png
            output_filename = os.path.splitext(filename)[0] + '.png'
            output_path = os.path.join(output_folder, output_filename)

            try:
                # 打开并转换图像
                with Image.open(input_path) as img:
                    # 保存为PNG格式
                    img.save(output_path, 'PNG')
                print(f'已转换: {filename} -> {output_filename}')
            except Exception as e:
                print(f'转换 {filename} 时出错: {str(e)}')


# 使用示例
input_folder = r"E:\data\人居数据\01建成区+临桂区\output"  # 替换为你的输入文件夹路径
output_folder = r"E:\data\人居数据\01建成区+临桂区\img"  # 替换为你的输出文件夹路径
convert_tif_to_png(input_folder, output_folder)