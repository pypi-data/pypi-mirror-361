import os


class File(object):
    @staticmethod
    # 递归搜索指定文件夹下所有文件
    def walk(path, callback=None):
        file_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                abs_path = os.path.join(root, file)
                if callback:
                    abs_path = callback(abs_path)
                if abs_path:
                    file_list.append(abs_path)
        return file_list
