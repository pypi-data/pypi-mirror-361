from ZfileSDK.utils import ApiClient, CustomException

# # 示例用法
# client = ApiClient(base_url="https://gamemanagezfile.jingtanggame.com")
# try:
#     client.login(username="jtgame", password="HHhh2333")
#     print("登录成功，token:", client.token)
# except CustomException as e:
#     print(f"登录失败: {e.msg} (code: {e.code})")
# finally:
#     client.close()

with ApiClient(base_url="https://gamemanagezfile.jingtanggame.com") as client:
    try:
        client.login(username="jtgame", password="HHhh2333")
        print("登录成功，token:", client.token)
    except CustomException as e:
        print(f"登录失败: {e.msg} (code: {e.code})")

from ZfileSDK.front import UserInterface

user_interface = UserInterface(api_client=client)
