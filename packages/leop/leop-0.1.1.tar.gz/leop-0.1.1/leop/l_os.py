def cin():
    a=input().split(' ')
    return a
def cout(a):
    for i in range(0,len(a)-1):
        print(a[i],end=' ')
    print(a[len(a)-1])
import subprocess

def cmd(command):
    try:
        # 执行系统命令并捕获输出
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # 返回标准输出内容
        return result.stdout
    except subprocess.CalledProcessError as e:
        # 命令执行失败时返回错误信息
        return f"Error: {e.stderr}"
    except Exception as e:
        # 处理其他异常
        return f"Exception: {str(e)}"    
import ctypes

def is_admin():
    """检查程序是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False