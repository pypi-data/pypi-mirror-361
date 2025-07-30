# MingChioY/cli/main.py
from importlib.resources import files
import shutil

import click
import os

cur_index = "init"
cur_file = "init.txt"
exclude_dir = ["__pycache__", "test", ".git", ".idea"]  # 排除的目录


def get_cli_path():
    # 获取包内的 "cli" 子目录
    cli_path = files("MingChioY") / "cli"

    # 转换为系统路径字符串
    return str(cli_path)


@click.group()
def main():
    pass


@main.command()
def hello():
    """Say hello."""
    print("hello")
    print("how to test locally?")
    print("first ,run \n\t pip install -e .")
    print("then you can test by command: mingchioy")
    print("after test please use: pip uninstall MingChioY")


@main.command()
def status():
    """
    Show the current status of the CLI tool.
    :return:
    """
    print(f"current index is: {cur_index}, current file is: {cur_file}")
    print(get_cli_path())


@main.command()
def get_indexes():
    """List all indexes."""
    print("Now you have the following indexes:\n")
    i = 0
    index = indexes()
    for idx in index:
        i += 1
        print(i, idx)


@main.command()
@click.argument("index_name")
def check_out_index(index_name):
    """
    check out an index.
    @param index_name: The name of the index to check out.
    """
    global cur_index
    path = get_cli_path()
    is_checked_out = False
    if index_name in os.listdir(path):
        full_path = os.path.join(path, index_name)
        if os.path.isdir(full_path) and index_name not in exclude_dir:
            cur_index = index_name
            is_checked_out = True
            print(f"Checked out to Index: {cur_index}")
    if not is_checked_out:
        print("********************************************")
        print("no such index, fail!")
        print(f"current Index is {cur_index}, have the following indexes: {indexes()}")


@main.command()
@click.argument("index_name")
def insert_indexes(index_name):
    """
    Insert a new index.
    @param index_name: The name of the new index to create.
    """
    index = indexes()
    if index_name not in index:
        global cur_index
        path = get_cli_path()
        new_index_path = os.path.join(path, index_name)

        os.makedirs(new_index_path)
        cur_index = index_name
        print(f"New Index '{cur_index}' created successfully. Auto check out!")
    else:
        print("********************************************")
        print("Index already exists, fail!")


@main.command()
@click.argument("index_name")
def delete_index(index_name):
    """
    Delete an index.
    @param index_name: The name of the index to delete.
    """
    path = get_cli_path()
    full_path = os.path.join(path, index_name)

    if os.path.isdir(full_path) and index_name not in exclude_dir:
        is_true = input("Are you sure you want to delete this index? (y/n): ")
        if is_true.lower() != 'y':
            print("Deletion cancelled.")
            return
        try:
            os.rmdir(full_path)
            global cur_index
            if cur_index == index_name:
                cur_index = ""
            print(f"Index '{index_name}' deleted successfully.")
        except OSError as e:
            print(f"Error deleting index '{index_name}': {e}")
    else:
        print("********************************************")
        print("Index does not exist or cannot be deleted!")


@main.command()
@click.argument("keyword")
def search(keyword):
    """
    Search for a keyword in current file.
    @param keyword: The keyword to search for in the current file.
    """
    if cur_index == "" or cur_file == "":
        print("Index or File was deleted, please check out another index!")
        return
    file_path = os.path.join(get_cli_path(), cur_index, cur_file)
    print(f"Search from Index: {cur_index}, File: {cur_file}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        found = False
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                print(f"Line {i + 1}: {line.strip()}")
                found = True

        if not found:
            print(f"No occurrences of '{keyword}' found in the file.")

    except FileNotFoundError:
        print(f"Error: File {cur_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


@main.command()
@click.argument("text")
def insert(text):
    """
    Append text to the end of Your File.
    @param text: The text to append to the current file.
    """
    if cur_index == "" or cur_file == "":
        print("Index or File was deleted, please check out another index!")
        return
    file_path = os.path.join(get_cli_path(), cur_index, cur_file)
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(text + '\n')
        print(f"Successfully appended: '{text}' to Index: {cur_index}, File: {cur_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


@main.command()
@click.argument("filename")
def check_out_file(filename):
    """
    Check out a file from the current index.
    :param filename: The name of the file to check out.
    """
    txt_files = list_all_txt_files_with_scandir()
    if filename in txt_files:
        global cur_file
        cur_file = filename
    else:
        print("********************************************")
        print("no such file, fail!")
        print(f"current Index is {cur_index}, have the following files: {txt_files}")


@main.command()
@click.argument("filename")
def insert_file(filename):
    """
    Insert a new file into the current index.
    :param filename:
    :return:
    """
    txt_files = list_all_txt_files_with_scandir()
    if filename in txt_files:
        print("********************************************")
        print("File already exists, fail!")
    else:
        file_path = os.path.join(get_cli_path(), cur_index, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")  # 创建一个空文件
            global cur_file
            cur_file = filename
            print(f"New File '{cur_file}' created successfully. Auto check out!")
        except Exception as e:
            print(f"An error occurred while creating the file: {e}")


@main.command()
@click.argument("filename")
def delete_file(filename):
    """Delete a file."""
    file_path = os.path.join(get_cli_path(), cur_index, filename)
    if os.path.isfile(file_path):
        is_true = input("Are you sure you want to delete this file? (y/n): ")
        if is_true.lower() != 'y':
            print("Deletion cancelled.")
            return
        try:
            os.remove(file_path)
            global cur_file
            if cur_file == filename:
                cur_file = ""
            print(f"File '{filename}' deleted successfully.")
        except OSError as e:
            print(f"Error deleting file '{filename}': {e}")
    else:
        print("********************************************")
        print("File does not exist or cannot be deleted!")


@main.command()
@click.argument("target_path")
def download(target_path):
    current_dir = get_cli_path()
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    # 遍历当前目录下的所有子项
    for item in os.listdir(current_dir):
        full_path = os.path.join(current_dir, item)
        # 只处理目录，且不是排除的目录
        if os.path.isdir(full_path) and item not in exclude_dir:
            dest_path = os.path.join(target_path, item)

            # 如果目标位置已有同名文件夹，先删除
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)

            print(f"Copying {item} to {dest_path}")
            shutil.copytree(full_path, dest_path)

    print("✅ All directories have been copied.")


def list_all_txt_files_with_scandir():
    # 获取当前工作目录
    current_directory = os.path.join(get_cli_path(), cur_index)

    # 使用 scandir 来遍历并过滤 .txt 文件
    with os.scandir(current_directory) as entries:
        txt_files = [entry.name for entry in entries if entry.is_file() and entry.name.endswith('.txt')]

    return txt_files


def indexes():
    path = get_cli_path()
    index = []

    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        if os.path.isdir(full_path) and name not in exclude_dir:
            index.append(name)
    return index


if __name__ == "__main__":
    main()
