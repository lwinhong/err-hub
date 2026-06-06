import debugpy

# 启动 debugpy 监听，等待 IDE 连接
# 也可改为 debugpy.listen(("0.0.0.0", 5678)) 让远程 IDE 连接
debugpy.listen(5678)
print("Debugpy listening on port 5678. Waiting for debugger to attach...")
debugpy.wait_for_client()
print("Debugger attached!")

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
