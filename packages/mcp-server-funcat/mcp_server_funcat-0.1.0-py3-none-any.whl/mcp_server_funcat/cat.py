import requests
from enum import Enum

# ["cute", "cat", "kitten", "funny", "fluffy", "sleepy", "grumpy", "playful", "sleepy cat", "black cat", "tabby", "tuxedo", "happy", "angry", "silly", "curious", "relaxed", "sleepy kitty", "adorable", "mischievous"]
class Tag(str, Enum):
    cute = "cute"
    cat = "cat"
    kitten = "kitten"
    funny = "funny"
    fluffy = "fluffy"
    sleepy = "sleepy"
    grumpy = "grumpy"
    playful = "playful"
    sleepy_cat = "sleepy cat"
    black_cat = "black cat"
    tabby = "tabby"
    tuxedo = "tuxedo"
    happy = "happy"
    angry = "angry"
    silly = "silly"
    curious = "curious"
    relaxed = "relaxed"
    sleepy_kitty = "sleepy kitty"
    adorable = "adorable"
    mischievous = "mischievous"


def get_funcat_url(text_to_say: str | None, tag: Tag=None) -> str | None:
    """
    从CATAAS API获取第一只猫的ID，并构建一个带文字的稳定URL。
    支持通过tag进行过滤
    """
    api_url = "https://cataas.com/api/cats"
    params = {}
    if tag:
        params['tags'] = tag

    try:
        # 发送GET请求
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # 如果请求失败 (如 404, 500)，则会抛出异常

        # 解析JSON数据
        cats_data = response.json()

        # 检查返回的数据是否为空
        if not cats_data:
            print("API没有返回任何猫咪数据。")
            return None

        # 获取第一只猫的ID
        first_cat_id = cats_data[0]['id']
        print(f"成功获取到猫咪ID: {first_cat_id}")

        cat_url = f"https://cataas.com/cat/{first_cat_id}"
        if text_to_say:
            cat_url = cat_url+ f"/says/{text_to_say}"
        return cat_url

    except requests.exceptions.RequestException as e:
        print(f"请求API时发生错误: {e}")
        return None

if __name__ == "__main__":
    text = "hello, world!"
    tag = "cute"
    final_url = get_funcat_url(text, tag)

    if final_url:
        print(f"URL是: {final_url}")
    else:
        print("未能获取到有效的猫咪图片URL。")