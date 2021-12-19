import base64
import json
import time
import rsa

import requests
from bs4 import BeautifulSoup

with open('config.json', encoding='utf-8') as f:
    config = json.load(f)

username = config['username']
password = config['password']
coursenumber = config['coursenumber']
teachernumber = config['teachernumber']
cookie = config['cookie']
notify = config['notify']
tgbotkey = config['tgbotkey']


class User:
    loginurl = 'https://oauth.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2Mzk5MjQ1MzUwMzgwNDE3NDMsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6InlSUUxKZlVzeDMyNmZTZUtOVUN0b29LdyIsInNjb3BlIjoiIiwicmVkaXJlY3RVcmkiOiJodHRwOi8veGsuYXV0b2lzcC5zaHUuZWR1LmNuL3Bhc3Nwb3J0L3JldHVybiIsInN0YXRlIjoiIn0= '

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
        'Cookie': cookie
    }

    def __init__(self, username, password):
        self.cookie = None
        self.username = username
        self.password = password

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
            f'https://oauth.shu.edu.cn/oauth/authorize?client_id=yRQLJfUsx326fSeKNUCtooKw&response_type=code&scope=&redirect_uri=http%3A%2F%2Fxk.autoisp.shu.edu.cn%2Fpassport%2Freturn&state={state}')
        self.cookie = sess.cookies


class Course:
    base = 'http://xk.autoisp.shu.edu.cn'
    query = base + '/StudentQuery/QueryCourseList'
    select = base + '/CourseSelectionStudent/CourseSelectionSave'
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


if __name__ == '__main__':
    User1 = User(username, password)
    User1.login()
    print(User.header)
