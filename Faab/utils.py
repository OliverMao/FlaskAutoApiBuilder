import flask
from flask_cors import *
from flask import request

import os

import json

from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import subprocess
import os

from werkzeug.utils import secure_filename
import base64

import datetime
import random

import os
from PIL import ImageColor, Image, ImageDraw
import ffmpeg


def upload(file, app=None, path=None):
    """
        上传文件并保存到指定路径

        Args:
            file (File): 要上传的文件对象
            app (Flask App, optional): Flask应用对象，默认为None
            path (str, optional): 文件保存路径，默认为None

        Returns:
            str: 文件的保存路径

        Raises:
            'No file selected': 当没有选择文件时抛出
            'app' was not delivered: 当没有提供app对象时抛出
    """
    # 检查文件是否存在
    if file.filename is None:
        return 'No file selected', 400
    if path is None:
        path = os.path.join(app.root_path, 'static')
        if app is None:
            return "'app' was not delivered", 400
    # 保存文件到指定路径
    file_path = os.path.join(path, file.filename)
    file.save(file_path)

    return file_path


def faab_compress_image(file, path=None, app=None, quality=100, format_=None):
    """
       压缩图像文件。

       参数：
       file: 上传的文件
       path: 保存文件的路径，默认为None
       app: Flask应用对象，默认为None
       quality: 压缩质量，默认为100
       format_: 图像格式，默认为None

       返回：
       字符串：压缩后的文件路径
       整数：HTTP状态码

       提供了一个压缩图像文件的函数。首先检查是否选择了文件，然后确定保存文件的路径（默认为'app.root_path/static'），然后再检查是否提供了Flask应用对象。接下来，检查文件类型是否是图像文件，并进行相应的压缩处理。如果文件类型不是图像文件或者文件大小超过了限制，将返回相应的错误信息。最后，返回压缩后的文件路径和HTTP状态码。
   """
    if file.filename is None:
        return "No selected file.", 400
    if path is None:
        path = os.path.join(app.root_path, 'static')
        if app is None:
            return "'app' was not delivered", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(path, filename)
        file.save(file_path)
        # 检查文件类型并进行相应的压缩处理
        if is_image_file(filename):
            if check_file_size(file):
                compress_image(file_path, quality, format_)
                return file_path
            else:
                return 'Invalid file or file size is too large.', 400
        elif is_video_file(filename):
            return 'Invalid file or file size is too large.', 400
    else:
        return 'Unsupported file type', 400


def faab_compress(path, file, quality=100, crf=0):
    """
        使用指定的路径、质量和常量比特率（CRF）压缩给定的文件。

        参数:
            path (str): 文件所在的路径。
            file (file): 要压缩的文件。
            quality (int, 可选): 压缩的品质设置。默认为100。
            crf (int, 可选): 压缩的常量比特率设置。默认为0。

        返回:
            dict: 压缩结果的字典。如果压缩成功，包括压缩后的文件路径。
    """
    # 检查上传的文件是否为图片或视频
    compressed_filename = ''
    if file.filename == '':
        # return 'No selected file', 400
        resu = {'code': 0, 'message': 'No selected file.'}
        return resu

    if file and allowed_file(file.filename):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(path, filename)
            file.save(file_path)
            # 检查文件类型并进行相应的压缩处理
            if is_image_file(filename):
                if check_file_size(file):
                    compressed_filename = compress_image(file_path, path, quality)
                else:
                    resu = {'code': 0, 'message': 'Invalid file or file size is too large.'}
                    return resu
            elif is_video_file(filename):
                compressed_filename = compress_video(file_path, path, crf)
        else:
            # return 'Unsupported file type', 400
            resu = {'code': 0, 'message': 'Unsupported file type.'}
            return resu
        # 压缩后的文件保存路径
        compressed_file_path = os.path.join(path, compressed_filename)
        # 返回压缩后的文件路径
        os.remove(file_path)
        resu = {'code': 1, 'path': compressed_file_path}
        return resu
    else:
        resu = {'code': 0, 'message': 'Invalid file or file size is too large.'}
        return resu


def allowed_file(filename):
    # 检查文件扩展名是否被允许
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def is_image_file(filename):
    # 检查文件是否为图片
    image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in image_extensions


def is_video_file(filename):
    # 检查文件是否为视频
    video_extensions = {'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in video_extensions


def compress_image(file_path, quality, format_):
    # 使用Pillow库压缩图片
    image = Image.open(file_path)
    # 计算调整后的高度
    # 转换为RGB模式
    if format_ == 'PNG':
        image = image.convert('RGBA')
        file_path_split = file_path.split('.')
        file_path = file_path_split[0] + '.png'
    elif format_ == 'JPEG':
        image = image.convert('RGB')
        file_path_split = file_path.split('.')
        file_path = file_path_split[0] + '.jpg'
    elif format_ == 'WEBP':
        image = image.convert('RGB')
        file_path_split = file_path.split('.')
        file_path = file_path_split[0] + '.webp'
    else:
        image = image.convert('RGB')
    image.save(file_path, optimize=True, quality=quality, format=format_, )
    return file_path


def compress_video(file_path, path, crf):
    # 使用FFmpeg库压缩视频
    now_date = datetime.datetime.now()
    now_date = datetime.datetime.strftime(now_date, '%Y-%m-%d-%H:%M:%S')
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    char_1 = random.choice(alphabet)
    char_2 = random.choice(alphabet)
    output_file = now_date + char_1 + char_2 + '.mp4'
    compressed_file_path = os.path.join(path, output_file)
    ffmpeg.input(file_path).output(compressed_file_path, crf=crf).run()
    # subprocess.run(['ffmpeg', '-i', file_path, '-vf', 'scale=640:480', '-c:v', 'libx264', '-crf', '23', compressed_file_path])
    return output_file


# 检查文件是否允许上传
def allowed_file(filename):
    # 在此处添加允许的文件类型检查逻辑
    # 例如，检查文件扩展名或MIME类型
    return True


# 检查文件大小是否超过限制
def check_file_size(file):
    # 设置文件大小限制（以字节为单位）
    max_size = 3 * 1024 * 1024  # 10MB

    # 获取文件大小
    file_size = len(file.read())
    file.seek(0)  # 将文件指针重置为开头

    # 检查文件大小是否超过限制
    if file_size > max_size:
        return False
    else:
        return True
