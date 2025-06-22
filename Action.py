import pandas as pd
import os
from datetime import datetime

class ExcelProcessor:
    def __init__(self):
        self.file_path = None
        self.file_info = {
            'name': '',
            'size': '',
            'modified_date': ''
        }
    
    def set_file(self, file_path):
        """设置要处理的文件路径"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        self.file_path = file_path
        self._update_file_info()
    
    def _update_file_info(self):
        """更新文件基本信息"""
        if not self.file_path:
            return
            
        # 获取文件状态
        stat = os.stat(self.file_path)
        
        # 文件名
        self.file_info['name'] = os.path.basename(self.file_path)
        
        # 文件大小 (转换为KB/MB)
        size = stat.st_size
        if size < 1024:
            self.file_info['size'] = f"{size} B"
        elif size < 1024*1024:
            self.file_info['size'] = f"{size/1024:.2f} KB"
        else:
            self.file_info['size'] = f"{size/(1024*1024):.2f} MB"
        
        # 修改日期
        timestamp = stat.st_mtime
        self.file_info['modified_date'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def to_markdown(self):
        """将Excel数据转换为Markdown表格"""
        if not self.file_path:
            raise ValueError("未设置文件路径")
            
        try:
            # 读取Excel文件
            df = pd.read_excel(self.file_path)
            
            # 转换为Markdown表格
            markdown_table = df.to_markdown(index=False)
            
            return markdown_table
        except Exception as e:
            raise Exception(f"转换Markdown失败: {str(e)}")
    
    def get_file_info(self):
        """获取文件基本信息"""
        return self.file_info

    @staticmethod
    def find_excel_files(directory):
        """查找目录中的Excel文件"""
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"无效的目录: {directory}")
            
        excel_files = []
        for file in os.listdir(directory):
            if file.lower().endswith(('.xlsx', '.xls')):
                excel_files.append(os.path.join(directory, file))
                
        return excel_files