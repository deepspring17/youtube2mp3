from flask import Flask
from flask import request
import traceback
import random

from src.crawlers.snapinsta import snapinsta
from src.crawlers.saveinsta import saveinsta
from src.crawlers.instasave import instasave

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/test")
def hello_test():
    return "<p>Hello, test!</p>"


@app.route("/api/v1/remove_watermark", methods=['POST'])
def remove_watermark():
    print(request.json, request.remote_addr, get_user_ip(request))
    url = request.json.get('url', '')
    if url == '' or 'instagram' not in url:
        return error_json(-1, "invalid_request")

    method = request.json.get('method', '')
    available_methods = ['snapinsta', 'instasave']
    return get_no_watermark_url(url, method, available_methods)


def get_no_watermark_url(url: str, method: str, available_methods):
    if not available_methods:
        print("error! no available method")
        return error_json(-1, 'Internal Error')
    # 请求未指定具体爬虫 则随机选择一个
    if method not in available_methods:
        method = random.choice(available_methods)
    available_methods.remove(method)
    try:
        return get_no_watermark_url_by_method(url, method)
    except Exception as e:
        print("Exception!!!", e)
        traceback.print_exc()
        return get_no_watermark_url(url, method, available_methods)


def get_no_watermark_url_by_method(url: str, method: str):
    if method == 'snapinsta':
        print('try snapinsta...')
        down_info = snapinsta.Snapinsta(url)
        return success_json(down_info)
    elif method == 'saveinsta':
        print('try saveinsta...')
        down_info = saveinsta.Saveinsta(url)
        return success_json(down_info)
    elif method == 'instasave':
        print('try instasave...')
        down_info = instasave.Instasave(url)
        return success_json(down_info)
    else:
        print("error! unknown method")
        return error_json(-1, 'Internal Error')


def error_json(code, msg):
    return {"code": code, "msg": msg}


def success_json(data):
    return {"code": 0, "msg": "ok", "data": data}


def get_user_ip(request):
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For']
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


if __name__ == "__main__":
    app.run()
