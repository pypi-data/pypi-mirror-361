import os
from mcp.server.fastmcp import FastMCP

# ==============================================================================
# 1. 初始化 MCP 服务器
# ==============================================================================
mcp = FastMCP("Aylixos App Workspace File Creator")

# ==============================================================================
# 2. 定义自定义功能函数
# ==============================================================================
# TARGET_DIR = "D:/temp-file"

# 同样，我们先定义一个标准的 Python 函数
@mcp.tool()
def create_file_in_temp(filename: str, worker_path: str, content: str = "") -> str:
    """
    filename: 文件名称
    worker_path: 文件路径
    content: 文件内容
    """
    print(f"收到创建文件请求: 文件名='{filename}', 文件路径='{worker_path}', 内容='{content[:30]}...'")

    try:
        if not os.path.exists(worker_path):
            os.makedirs(worker_path)
            print(f"目标目录 '{worker_path}' 不存在，已自动创建。")
    except Exception as e:
        error_message = f"错误：创建目标目录 '{worker_path}' 失败: {e}"
        print(error_message)
        return error_message

    if ".." in filename or "/" in filename or "\\" in filename:
        error_message = f"错误：文件名 '{filename}' 包含非法字符，操作被拒绝。"
        print(error_message)
        return error_message

    try:
        full_path = os.path.join(worker_path, filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        success_message = f"成功：文件 '{full_path}' 已成功创建。"
        print(success_message)
        return success_message
    except Exception as e:
        error_message = f"错误：在 '{worker_path}' 目录下创建文件 '{filename}' 失败: {e}"
        print(error_message)
        return error_message

def main() -> None:
    mcp.run(transport='stdio')
