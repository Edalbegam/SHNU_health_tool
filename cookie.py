from bs4 import BeautifulSoup
from pathlib import Path
import requests
import execjs
import time


USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
RETRY_TIMEOUT = 5
RETRY = 5

requests.packages.urllib3.disable_warnings()


#编译加密程序
def get_js(jsfile):
    try:
        f=open(Path(__file__).resolve().parent.joinpath(jsfile), encoding='utf8')
        line=f.readline()
        htmlstr=''
        while line:
            htmlstr=htmlstr+line
            line=f.readline()
        ctx=execjs.compile(htmlstr)
        return ctx
    except:
        print("----缺少必要文件“des.js”或文件损坏,请检查当前目录\n")
        raise
    

def get_asp_net_sessionid():
    for _ in range(RETRY):
        try:
            response=requests.get(url="https://yqfk.shnu.edu.cn/LoginSSO.aspx?ReturnUrl=%2f",verify=False,allow_redirects=False)
            asp_net_sessionid=response.headers['Set-Cookie'].split(';')[0]
        except:
            time.sleep(RETRY_TIMEOUT)
            continue
        else:
            print("----起始页获取完成\n")
            return asp_net_sessionid
    else:
        print('----获取每日一报起始页超时\n')
        raise


def get_cas_page():
    for _ in range(RETRY):
        try:
            response=requests.get(url="https://cas.shnu.edu.cn/cas/login?service=https://yqfk.shnu.edu.cn/LoginSSO.aspx",verify=False,allow_redirects=False)
            jessionid=response.headers["Set-Cookie"].split('; ')[3].split(', ')[-1]    
            body=BeautifulSoup(response.text, 'html.parser')
            lt=body.find('input', attrs={'name': 'lt'})['value']
            execution=body.find('input', attrs={'name': 'execution'})['value'] 
        except:
            time.sleep(RETRY_TIMEOUT)
            continue
        else:
            print("----CAS认证页面解析完成\n")
            return jessionid,lt,execution
    else:
        print('----访问CAS认证系统超时\n')
        raise


#多次后有概率认证失败(服务端机制)
def get_location(jessionid,ctx,username,password,lt,execution):
    print("----开始认证用户信息："+username+"\n")
    rsa=ctx.call('strEnc',username+password+lt,'1','2','3')
    headers={
        'Cookie':jessionid,
        'Content-Type':'application/x-www-form-urlencoded',
        'Connection':'close',
        'User-Agent':USER_AGENT
    }
    data={
        'rsa':rsa,
        'ul':len(username),
        'pl':len(password),
        'lt':lt,
        'execution':execution,
        '_eventId':'submit'
    }
    for _ in range(RETRY):
        try:
            location=requests.post(url="https://cas.shnu.edu.cn/cas/login?service=https://yqfk.shnu.edu.cn/LoginSSO.aspx",verify=False,allow_redirects=False,headers=headers,data=data).headers['Location']
            if "ticket=" not in location:
                time.sleep(RETRY_TIMEOUT)
                continue
        except:
            time.sleep(RETRY_TIMEOUT)
            continue
        else:
            print('----CAS认证成功！\n')
            return location
    else:
        print('----CAS认证失败，用户名/密码错误 或操作太频繁')
        raise


def get_ncov2019selfreport_shnu(location,asp_net_sessionid):
    headers={
        'Cookie':asp_net_sessionid,
        'User-Agent':USER_AGENT
    }
    for _ in range(RETRY):
        try:
            response=requests.get(url=location,verify=False,allow_redirects=False,headers=headers)
            ncov2019selfreport_shnu=response.headers['Set-Cookie'].split(';')[0]
        except:
            time.sleep(RETRY_TIMEOUT*2)
            continue
        else:
            print('----健康之路登陆成功！\n')
            return ncov2019selfreport_shnu
    else:
        print('----健康之路登录超时\n')
        raise


def get_viewstate(asp_net_sessionid,ncov2019selfreport_shnu,BaoSRQ):
    headers={
        'Cookie':asp_net_sessionid+';'+ncov2019selfreport_shnu,
        'User-Agent':USER_AGENT
    }
    for _ in range(RETRY):
        try:
            response=requests.get(url="https://yqfk.shnu.edu.cn/ViewDayReport.aspx?day="+BaoSRQ,verify=False,allow_redirects=False,headers=headers)
            if "无指定日期的信息" in response.text: flag=0
            else: flag=1
            response=requests.get(url="https://yqfk.shnu.edu.cn/DayReport.aspx",verify=False,allow_redirects=False,headers=headers)
            body = BeautifulSoup(response.text, 'html.parser')
            viewstate=body.find('input', attrs={'id': '__VIEWSTATE'})['value']
        except:
            time.sleep(RETRY_TIMEOUT)
            continue
        else:
            print('----日报状态获取完成\n')
            if flag==0: print('----今天还未进行填报\n')
            elif flag==1: print('----今天已进行过填报，将覆盖原有填报信息\n')
            return viewstate
    else:
        print('----获取日报状态超时\n')
        raise


def post_report(asp_net_sessionid,ncov2019selfreport_shnu,viewstate,BaoSRQ,ShiFSH,ShiFZX,ddlSheng,ddlShi,ddlXian,XiangXDZ,ShiFZJ,fstate):
    print('----开始上传填报信息...\n')
    headers={
        'Cookie':asp_net_sessionid+';'+ncov2019selfreport_shnu,
        'User-Agent':USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
        'X-FineUI-Ajax': 'true',
        'Connection':'close',
    }
    data={
        "__EVENTTARGET":"p1$ctl01$btnSubmit",
        "__EVENTARGUMENT":"",
        "__VIEWSTATE":viewstate,
        "__VIEWSTATEGENERATOR":"7AD7E509",
        "p1$ChengNuo":"p1_ChengNuo",
        "p1$BaoSRQ":BaoSRQ,
        "p1$DangQSTZK":"良好",
        "p1$TiWen":"",
        "p1$pImages$HFimgSuiSM":"",
        "p1$pImages$HFimgXingCM":"",
        "p1$GuoNei":"国内",
        "p1$ddlGuoJia$Value":"-1",
        "p1$ddlGuoJia":"选择国家",
        "p1$ShiFSH":ShiFSH,
        "p1$ShiFZX":ShiFZX,
        "p1$ddlSheng$Value":ddlSheng,
        "p1$ddlSheng":ddlSheng,
        "p1$ddlShi$Value":ddlShi,
        "p1$ddlShi":ddlShi,
        "p1$ddlXian$Value":ddlXian,
        "p1$ddlXian":ddlXian,
        "p1$XiangXDZ":XiangXDZ,
        "p1$ShiFZJ":ShiFZJ,
        "p1$FengXDQDL":"否",
        "p1$TongZWDLH":"否",
        "p1$JieChu":"否",
        "p1$QueZHZJC$Value":"否",
        "p1$QueZHZJC":"否",
        "p1$DangRGL":"否",
        "p1$GeLDZ":"",
        "p1$FanXRQ":"",
        "p1$WeiFHYY":"",
        "p1$ShangHJZD":"",
        "p1$DaoXQLYGJ":"",
        "p1$DaoXQLYCS":"",
        "p1$JiaRen_BeiZhu":"",
        "p1$SuiSM":"绿色",
        "p1$LvMa14Days":"是",
        "p1$Address2":"",
        "p1$BeiZhu":"",
        "F_TARGET":"p1_ctl01_btnSubmit",
        "p1_pImages_Collapsed":"false",
        "p1_ContentPanel1_Collapsed":"true",
        "p1_GeLSM_Collapsed":"false",
        "p1_Collapsed":"false",
        "F_STATE":fstate,
        "X-FineUI-Ajax":"true"
    }
    for _ in range(RETRY):
        try:
            response=requests.post(url="https://yqfk.shnu.edu.cn/DayReport.aspx",verify=False,allow_redirects=False,headers=headers,data=data).text
        except:
            time.sleep(RETRY_TIMEOUT)
            continue
        else:
            if '请正确填写当天是否在上海、是否住校' in response:
                print("----日报信息提交失败，请正确填写当天是否在上海、是否住校\n")
                raise
            elif '请正确填写当天是否在上海及当天所在省市' in response:
                print("----日报信息提交失败，请正确填写当天是否在上海及当天所在省市\n")
                raise
            elif '凌晨零点至1点，系统维护中，暂停日报' in response:
                print("----日报信息提交失败。凌晨零点至1点，系统维护中，暂停日报\n")
                raise
            elif '日报信息提交成功' in response:
                return True
            else:
                print(response)
                raise
    else:
        print('----获取日报提交结果超时\n')
        raise