import os
import shutil
from PIL import Image
from pyzjr.data.utils.path import get_image_path

def batch_modify_images(
        target_path,
        save_path,
        start_index=None,
        prefix='',
        suffix='',
        format=None,
        target_shape=None,
        num_type=1,
):
    """
    重命名图像文件夹中的所有图像文件并保存到指定文件夹
    :param target_path: 目标文件路径
    :param save_path: 文件夹的保存路径
    :param start_index: 默认为 1, 从多少号开始
    :param prefix: 重命名的通用格式前缀, 如 rename001.png, rename002.png...
    :param suffix: 重命名的通用格式后缀, 如 001rename.png, 002rename.png...
    :param format (str): 新的后缀名，不需要包含点（.）
    :param num_type: 数字长度, 比如 3 表示 005
    """
    os.makedirs(save_path, exist_ok=True)
    images_paths = get_image_path(target_path)

    for i, image_path in enumerate(images_paths):
        image_name = os.path.basename(image_path)
        name, ext = os.path.splitext(image_name)
        re_ext = f".{format}" if format is not None else ext
        if start_index:
            padded_i = str(start_index).zfill(num_type)
            start_index += 1
        else:
            padded_i = name
        new_image_name = f"{prefix}{padded_i}{suffix}{re_ext}"
        new_path = os.path.join(save_path, new_image_name)
        image = Image.open(image_path).convert('RGB')
        if target_shape:
            height, width = target_shape
            image = image.resize((width, height))
        image.save(new_path)
        print(f"{i + 1} Successfully rename {image_path} to {new_path}")

def copy_files_to_save_folder(target_path, save_folder):
    """
    将多个文件复制到指定保存文件夹

    Args:
        target_path (list): 需要复制的文件路径列表（如 [path1, path2, ...]）
        save_folder (str): 目标保存文件夹路径
    """
    try:
        os.makedirs(save_folder, exist_ok=True)
        for img_path in target_path:
            base_file_name = os.path.basename(img_path)
            destination_path = os.path.join(save_folder, base_file_name)
            shutil.copy2(img_path, destination_path)
            print(f"Successfully copied: {img_path} -> {save_folder}")
    except Exception as e:
        print(f"Error copying files: {e}")
