import base64
import time
import rsa
import requests
from bs4 import BeautifulSoup

# URL
base = 'http://xk.autoisp.shu.edu.cn'
queryurl = base + '/StudentQuery/QueryCourseList'
verifyurl = base + '/CourseSelectionStudent/VerifyDiffCampus'
selecturl = base + '/CourseSelectionStudent/CourseSelectionSave'
termurl = base + '/Home/TermSelect'
termindex = base + '/Home/TermIndex'


class User:
    username = None
    password = None
    term = None
    sess = None
    url = 'https://oauth.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2Mzk5MjQ1MzUwMzgwNDE3NDMsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6InlSUUxKZlVzeDMyNmZTZUtOVUN0b29LdyIsInNjb3BlIjoiIiwicmVkaXJlY3RVcmkiOiJodHRwOi8veGsuYXV0b2lzcC5zaHUuZWR1LmNuL3Bhc3Nwb3J0L3JldHVybiIsInN0YXRlIjoiIn0= '
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
        'Cookie': ''
    }

    def __init__(self, username=None, password=None, term=None):
        self.username = username
        self.password = password
        self.term = term

    def login(self):
        self.sess = requests.Session()
        r = self.sess.get(base)
        code = r.url.split('/')[-1]
        url_param = eval(base64.b64decode(code).decode("utf-8"))
        state = url_param['state']
        self.sess.post(r.url, data={
            'username': self.username,
            'password': encryptPass(self.password)
        }, allow_redirects=False, headers=self.header)
        # self.sess.get(
        #     f'https://oauth.shu.edu.cn/oauth/authorize?client_id=yRQLJfUsx326fSeKNUCtooKw&response_type=code&scope=&redirect_uri=http%3A%2F%2Fxk.autoisp.shu.edu.cn%2Fpassport%2Freturn&state={state}')
        cookie_jar = self.sess.cookies
        cookie_t = requests.utils.dict_from_cookiejar(cookie_jar)
        self.header['Cookie'] = str('ASP.NET_SessionId=') + (cookie_t['ASP.NET_SessionId'])
        self.sess.get(termindex, headers=self.header)
        self.sess.post(termurl, data={
            'termId': self.term
        }, headers=self.header)


class Course:
    formdata = {'PageIndex': '1',
                'PageSize': '30',
                'FunctionString': 'Query',
                'CID': '',
                'CourseName': '',
                'IsNotFull': 'false',
                'CourseType': 'B',
                'TeachNo': '',
                'TeachName': '',
                'Enrolls': '',
                'Capacity1': '',
                'Capacity2': '',
                'CampusId': '',
                'CollegeId': '',
                'Credit': '',
                'TimeText': ''
                }

    selectdata = {'cids': '',
                  'tnos': ''}

    def __init__(self, cid=None, tid=None):
        self.formdata['CID'] = cid
        self.formdata['TeachNo'] = tid
        self.selectdata['cids'] = cid
        self.selectdata['tnos'] = tid


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


def queryCourse(user, course, idx):
    r = requests.post(queryurl, headers=user.header, data=course.formdata)
    if r.status_code != requests.codes.ok:
        print('4XX or 5XX Error, check your Internet connection or you cookie')
        return -1
    soup = BeautifulSoup(r.text, 'lxml')
    for each_course in soup.find_all('tr', attrs={'name': 'rowclass'}):
        # all_tr_tag = each_course.find_all('tr')
        all_td_tag = each_course.find_all('td', attrs={'style': 'text-align: center;'})
        plan = all_td_tag[1].text
        current = all_td_tag[2].text
        print("第" + str(idx) + "次尝试：")
        print("当前：" + current + "人，计划：" + plan + "人")
        if int(plan) > int(current):
            print("有空余，自动选课...")
            return 1
        else:
            print("无空余")
            print("1秒后继续查询课程人数...\n")
            time.sleep(1)
            return 0


def selectCourse(user, course):
    requests.post(verifyurl, data=course.selectdata, headers=user.header)
    r = requests.post(selecturl, data=course.selectdata, headers=user.header)
    soup = BeautifulSoup(r.text, 'lxml')
    if r.text.find('选课成功') > -1:
        print("选课成功！程序将退出。")
        return 1
    if r.text.find('教学班人数已满！') > -1:
        print("选课失败！原因是人数已满！将继续监控该课程。")
        return 0
    if r.text.find('已选此课程') > -1:
        print("选课失败！已选此课程！请登陆选课系统查看选课！\n为防止账号被风控，将停止监控该课程。")
        return -1
    if r.text.find('选课失败') > -1:
        print("选课失败！其他未知原因错误，请自行进入选课系统查看！将继续监控该课程。")
        return 0


if __name__ == '__main__':
    # TODO:Add support for storing confidential and ask user whether to use last time confidential
    username = input("请输入学号：")
    password = input("请输入密码：")
    term = input("请输入学期：（如2021-2022学年春季学期请输入20213）")

    user = User(username, password, term)
    user.login()

    cid = input("请输入课程号：")
    tid = input("请输入教师号：")

    course = Course(cid, tid)

    idx = 1
    while True:
        courseAvailable = queryCourse(user, course, idx)
        if courseAvailable == 1:
            selectStatus = selectCourse(user, course)
            if selectStatus == 1 or selectStatus == -1:
                break
            elif selectStatus == 0:
                time.sleep(5)
                continue
        if courseAvailable == -1:
            break
        idx = idx + 1