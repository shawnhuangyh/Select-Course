import base64
import json
import time
import rsa

import requests
from bs4 import BeautifulSoup

with open('config.json', encoding='utf-8') as f:
    config = json.load(f)

coursenumber = config['coursenumber']
teachernumber = config['teachernumber']


class User:
    username = config['username']
    password = config['password']
    loginurl = 'https://oauth.shu.edu.cn/login' \
               '/eyJ0aW1lc3RhbXAiOjE2Mzk5MjQ1MzUwMzgwNDE3NDMsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6InlSUUxKZlVzeDMyNmZTZUtOVUN0b29LdyIsInNjb3BlIjoiIiwicmVkaXJlY3RVcmkiOiJodHRwOi8veGsuYXV0b2lzcC5zaHUuZWR1LmNuL3Bhc3Nwb3J0L3JldHVybiIsInN0YXRlIjoiIn0= '

    def encryptPass(password):
        key_str = '''-----BEGIN PUBLIC KEY-----
        MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDl/aCgRl9f/4ON9MewoVnV58OL
        OU2ALBi2FKc5yIsfSpivKxe7A6FitJjHva3WpM7gvVOinMehp6if2UNIkbaN+plW
        f5IwqEVxsNZpeixc4GsbY9dXEk3WtRjwGSyDLySzEESH/kpJVoxO7ijRYqU+2oSR
        wTBNePOk1H+LRQokgQIDAQAB
        -----END PUBLIC KEY-----'''
        pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(key_str.encode('utf-8'))
        crypto = base64.b64encode(rsa.encrypt(password.encode('utf-8'), pub_key)).decode()
        return crypto

    def login(self):
        sess = requests.Session()
        r = sess.get(Course.base)
        code = r.url.split('/')[-1]
        url_param = eval(base64.b64decode(code).decode("utf-8"))
        state = url_param['state']
        sess.post(r.url, data={
            'username': self.username,
            'password': User.encryptPass(self.password)
        }, allow_redirects=False)
        sess.get(
            f'https://oauth.shu.edu.cn/oauth/authorize?client_id=yRQLJfUsx326fSeKNUCtooKw&response_type=code&scope'
            f'=&redirect_uri=http%3A%2F%2Fxk.autoisp.shu.edu.cn%2Fpassport%2Freturn&state={state}')
        Course.cookie = sess.cookies
        
        r = requests.get("http://xk.autoisp.shu.edu.cn/StudentQuery/QueryCourseList", headers=header)
        print(r.text)



class Course:
    base = 'http://xk.autoisp.shu.edu.cn'
    query = base + '/StudentQuery/QueryCourseList'
    select = base + '/CourseSelectionStudent/CourseSelectionSave'


cookie = config['cookie']
notify = config['notify']
tgbotkey = config['tgbotkey']

formdata = {'PageIndex': '1',
            'PageSize': '30',
            'FunctionString': 'Query',
            'CID': coursenumber,
            'CourseName': '',
            'IsNotFull': 'false',
            'CourseType': 'B',
            'TeachNo': teachernumber,
            'TeachName': '',
            'Enrolls': '',
            'Capacity1': '',
            'Capacity2': '',
            'CampusId': '',
            'CollegeId': '',
            'Credit': '',
            'TimeText': ''
            }

selectdata = {'cids': coursenumber,
              'tnos': teachernumber}

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    'Cookie': cookie
}

# def sendmessage(message):
#     if notify == 'true':
#         tg_bot_key, tg_chat_id = tgbotkey.split('@')
#         tgurl = 'https://api.telegram.org/bot%s/sendMessage' % tg_bot_key
#         data = {
#             'chat_id': tg_chat_id,
#             'text': message
#         }
#         r = requests.post(tgurl, data=data)
#         # print(r.text.find('ok'))
#
#
# def queryclass():
#     idx = 1
#     while True:
#         r = requests.post(queryurl, data=formdata, headers=header)
#         # print(r.text)
#         if r.status_code != requests.codes.ok:
#             print('4XX or 5XX Error,check your Internet connection or you cookie')
#             sendmessage('4XX or 5XX Error,check your Internet connection or you cookie')
#             time.sleep(10)
#             return False
#         soup = BeautifulSoup(r.text, 'lxml')
#         for each_course in soup.find_all('tr', attrs={'name': 'rowclass'}):
#             # all_tr_tag = each_course.find_all('tr')
#             all_td_tag = each_course.find_all('td', attrs={'style': 'text-align: center;'})
#             plan = all_td_tag[1].text
#             current = all_td_tag[2].text
#             print("第" + str(idx) + "次尝试：")
#             idx = idx + 1
#             print("当前：" + current + "人，计划：" + plan + "人")
#             if int(plan) > int(current):
#                 print("有空余，即将自动选课...")
#                 return True
#             else:
#                 print("无空余")
#                 print("1秒后继续查询课程人数...")
#                 print("====================\n")
#                 time.sleep(1)
#                 continue
#
#
# def selectclass():
#     r = requests.post(selecturl, data=selectdata, headers=header)
#     soup = BeautifulSoup(r.text, 'lxml')
#     if r.text.find('选课成功') > -1:
#         print("选课成功！程序将退出。")
#         sendmessage("选课成功！程序将退出。")
#         return True
#     if r.text.find('教学班人数已满！') > -1:
#         print("选课失败！原因是人数已满！将继续监控该课程。")
#         sendmessage("选课失败！原因是人数已满！将继续监控该课程。")
#         return False
#     if r.text.find('已选此课程') > -1:
#         print("选课失败！已选此课程！请登陆选课系统查看选课！\n为防止账号被风控，将停止停止监控该课程。")
#         sendmessage("选课失败！已选此课程！请登陆选课系统查看选课！\n为防止账号被风控，将停止监控该课程。")
#         return True
#     if r.text.find('选课失败') > -1:
#         print("选课失败！其他未知原因错误，请自行进入选课系统查看！将继续监控该课程。")
#         sendmessage("选课失败！其他未知原因错误，请自行进入选课系统查看！将继续监控该课程。")
#         return False
#

if __name__ == '__main__':
    # if notify == 'true':
    #     print("消息测试，请检查 Telegram 消息。")
    # sendmessage("Telegram 消息发送成功！")
    # while True:
    #     flag = queryclass()
    #     if flag == True:
    #         selectflag = selectclass()
    #         if selectflag == True:
    #             break
    #         if selectflag == False:
    #             print("1秒后继续查询课程人数...")
    #             print("====================\n")
    #             time.sleep(1)
    #             continue
    #     break
    User1 = User()
    User1.login()
