import base64
import urllib
import requests
import json
from PIL import Image
from PIL import ImageGrab
from io import BytesIO
import time
import os
import ctypes


def make(screen):
    save_pic(screen)
    while not os.path.exists("pic.png"):
        pass

    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    API_KEY = "YleMT041wl8zkXhk1Y4AdEuk"
    SECRET_KEY = "xQousjKEqphGwVMKHJlUSGDXp7PiUVpk"
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials",
              "client_id": API_KEY, "client_secret": SECRET_KEY}

    # 获取访问令牌并构建API请求URL
    access_token = str(requests.post(
        url, params=params).json().get("access_token"))
    create_url = f"https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2imgv2?access_token={access_token}"
    query_url = f"https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImgv2?access_token={access_token}"

    # 读取图像并转换为Base64编码
    with open("pic.png", "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')

    # 构建创建任务的请求参数
    create_payload = json.dumps({
        "prompt": "参考当前图，希望画面卡通一些，画面可以丰富一些，内容积极向上，参考宫崎骏画风",
        "width": 1024,
        "height": 1024,
        "image": base64_string,
        "change_degree": 1
    }, ensure_ascii=False)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # 发送创建任务请求
    response = requests.post(create_url, headers=headers,
                             data=create_payload.encode("utf-8"))
    response.raise_for_status()  # 检查请求是否成功
    task_id = response.json()["data"]["task_id"]
    # print(f"任务已创建，ID: {task_id}")

    # 轮询检查任务状态
    query_payload = json.dumps({"task_id": task_id}, ensure_ascii=False)
    task_status = "RUNNING"
    print("AI图片生成中.......")
    while task_status == "RUNNING":
        time.sleep(30)
        response = requests.post(
            query_url, headers=headers, data=query_payload.encode("utf-8"))
        response.raise_for_status()
        task_status = response.json()["data"]["task_status"]
        # print(f"任务状态: {task_status}")

    # 处理任务结果
    if task_status == "SUCCESS":
        picture = requests.get(response.json()[
                               "data"]["sub_task_result_list"][0]["final_image_list"][0]["img_url"])
        image_data = BytesIO(picture.content)
        image = Image.open(image_data)
        image.save('image.gif')
        os.system("image.gif")
    else:
        print(f"任务失败，状态: {task_status}")


def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded 
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content


def save_pic(screen, output_file="pic.png"):
    """
    精准截取turtle绘图区域，不包含窗口边框和标题栏
    专为Windows系统优化，支持高DPI缩放

    参数:
        screen: turtle的Screen对象
        output_file: 输出文件名
    """
    canvas = screen.getcanvas()
    screen.update()

    try:
        # 获取画布位置和大小
        x = canvas.winfo_rootx()
        y = canvas.winfo_rooty()
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        # 检测Windows屏幕缩放比例
        scale_factor = detect_windows_scale()
        # print(f"检测到屏幕缩放比例: {scale_factor}x")

        # 调整截图区域，排除窗口边框
        # 典型Windows窗口边框宽度约为8像素，标题栏约为30像素
        border_width = int(8 * scale_factor)
        title_height = int(30 * scale_factor)

        # 计算实际绘图区域
        img = ImageGrab.grab(
            bbox=(
                x + border_width,  # 左边界，排除左侧边框
                y + title_height,  # 上边界，排除标题栏和上边框
                x + width - border_width,  # 右边界，排除右侧边框
                y + height - border_width  # 下边界，排除底部边框
            )
        )

        # 保存为PNG
        img.save(output_file)
        # print(f"已保存图形到 {output_file} (尺寸: {img.size})")
    except Exception as e:
        print(f"截图时出错: {e}")
        print("提示: 尝试使用save_turtle_canvas_fallback函数或手动截图")


def detect_windows_scale():
    """
    检测Windows系统的屏幕缩放比例
    优先使用高精度方法，失败则降级使用兼容性方法
    """
    try:
        # 高精度方法：获取系统DPI
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()

        # 尝试获取系统DPI (Windows 8.1及以上)
        if hasattr(user32, 'GetDpiForSystem'):
            dpi = user32.GetDpiForSystem()
            return dpi / 96.0  # Windows标准DPI是96

        # 尝试获取显示器DPI (Windows 10及以上)
        if hasattr(user32, 'GetDpiForWindow'):
            root = tk.Tk()
            dpi = user32.GetDpiForWindow(root.winfo_id())
            root.destroy()
            return dpi / 96.0

        # 兼容方法：获取屏幕尺寸并与标准尺寸比较
        screen_width = user32.GetSystemMetrics(0)
        return screen_width / 1920.0  # 假设标准分辨率为1920x1080
    except Exception as e:
        print(f"检测缩放比例时出错: {e}")
        print("使用默认缩放比例1.0")
        return 1.0
