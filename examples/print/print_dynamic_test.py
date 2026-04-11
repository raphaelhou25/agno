import time
import sys
import itertools

# 1. 定义动画帧：这里使用的是盲文点阵字符，转起来非常平滑
spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
# itertools.cycle 可以让这个列表无限循环
spinner = itertools.cycle(spinner_frames)

print("准备开始处理任务...")

# 2. 模拟一个耗时 3 秒的下载任务
for i in range(30):
    frame = next(spinner)
    # \r 回到行首，打印当前的转圈符号，注意后面的空格用来覆盖旧字符
    sys.stdout.write(f"\r\033[36m{frame}\033[0m Fetching postgresql@14...")
    sys.stdout.flush()
    time.sleep(0.1) # 控制转圈的速度

# 3. 任务完成，打印绿色的对号
# \033[32m 是绿色，\033[0m 是重置颜色
sys.stdout.write("\r\033[32m✔\033[0m Fetching postgresql@14... Done!    \n")
sys.stdout.flush()

print("所有任务执行完毕。")
