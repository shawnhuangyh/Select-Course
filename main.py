import base64
import time
import rsa
import requests
from bs4 import BeautifulSoup


class User:
    username = None
    password = None
    term = None
    url = 'https://oauth.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2Mzk5MjQ1MzUwMzgwNDE3NDMsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6InlSUUxKZlVzeDMyNmZTZUtOVUN0b29LdyIsInNjb3BlIjoiIiwicmVkaXJlY3RVcmkiOiJodHRwOi8veGsuYXV0b2lzcC5zaHUuZWR1LmNuL3Bhc3Nwb3J0L3JldHVybiIsInN0YXRlIjoiIn0= '
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
        'Cookie': ''
    }


class Course:
    base = 'http://xk.autoisp.shu.edu.cn'
    query = base + '/StudentQuery/QueryCourseList'
    select = base + '/CourseSelectionStudent/CourseSelectionSave'
    term = base + '/Home/TermSelect'
    cid = None
    tid = None
    formdata = {'PageIndex': '1',
                'PageSize': '30',
                'FunctionString': 'Query',
                'CID': cid,
                'CourseName': '',
                'IsNotFull': 'false',
                'CourseType': 'B',
                'TeachNo': tid,
                'TeachName': '',
                'Enrolls': '',
                'Capacity1': '',
                'Capacity2': '',
                'CampusId': '',
                'CollegeId': '',
                'Credit': '',
                'TimeText': ''
                }

    selectdata = {'cids': cid,
                  'tnos': tid}


class Utli:
    sess = None

    def __init__(self, username=None, password=None, term=None):
        User.username = username
        User.password = password
        User.term = term

    def encryptPass(self, password):
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
        self.sess = requests.Session()
        r = self.sess.get(Course.base)
        code = r.url.split('/')[-1]
        url_param = eval(base64.b64decode(code).decode("utf-8"))
        state = url_param['state']
        self.sess.post(r.url, data={
            'username': User.username,
            'password': self.encryptPass(User.password)
        }, allow_redirects=False, headers=User.header)
        # self.sess.get(
        #     f'https://oauth.shu.edu.cn/oauth/authorize?client_id=yRQLJfUsx326fSeKNUCtooKw&response_type=code&scope=&redirect_uri=http%3A%2F%2Fxk.autoisp.shu.edu.cn%2Fpassport%2Freturn&state={state}')
        r = self.sess.post(Course.term, data={
            'termId': User.term
        }, allow_redirects=True, headers=User.header)
        cookie_jar = self.sess.cookies
        cookie_t = requests.utils.dict_from_cookiejar(cookie_jar)
        User.header['Cookie'] = str('ASP.NET_SessionId=') + (cookie_t['ASP.NET_SessionId'])

    def test(self):
        r = requests.get(Course.query, headers=User.header, data=Course.formdata)
        print(r.text)


if __name__ == '__main__':
    while True:
        print("1.设置用户")
        print("2.添加课程")
        print("3.开始选课")
        print("0.退出")

        i = input("请输入序号(0-3):")
        if i == '1':
            username = input("请输入学号：")
            password = input("请输入密码：")
            term = input("请输入学期：（如2021-2022学年春季学期请输入20213）")
            user = Utli(username, password, term)
            user.login()
            user.test()
        elif i == '2':
            print("test2")
        elif i == '3':
            print("test3")
        else:
            break
