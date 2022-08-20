from pathlib import Path
import datetime as dt
import execjs
import base64
import yaml
import json


def get_time():
    t = dt.datetime.utcnow()
    t = t + dt.timedelta(hours=8)
    # t = dt.datetime.now()
    BaoSRQ = t.strftime('%Y-%m-%d')
    return BaoSRQ


def generate_js(jsfile):
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


def get_config():
    print("----载入配置文件...\n")
    try:
        with open(Path(__file__).resolve().parent.joinpath('config.yaml'), encoding='utf8') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                username=config['学号']
                password=config['密码']
                ShiFSH=config['当天是否在上海']
                ShiFZX=config['当天是否住学校']
                ddlSheng=config['当天所在省']
                ddlShi=config['当天所在市']
                ddlXian=config['当天所在县区']
                XiangXDZ=config['详细地址']
                ShiFZJ=config['是否家庭地址']
    except:
        print("----配置文件载入失败！请检查config.yaml\n")
        raise
    else:
        print("----配置信息载入成功！\n")
        return username,password,ShiFSH,ShiFZX,ddlSheng,ddlShi,ddlXian,XiangXDZ,ShiFZJ


def generate_fstate(BaoSRQ, ShiFSH, ShiFZX, ddlSheng, ddlShi, ddlXian, XiangXDZ, ShiFZJ):
    try:
        with open(Path(__file__).resolve().parent.joinpath('fstate_origin.json'), encoding='utf8') as f:
                fstate = json.loads(f.read())
        fstate['p1_BaoSRQ']['Text'] = BaoSRQ
        fstate['p1_ShiFSH']['SelectedValue'] = ShiFSH
        fstate['p1_ShiFZX']['SelectedValue'] = ShiFZX
        fstate['p1_ddlSheng']['F_Items'] = [[ddlSheng, ddlSheng, 1, '', '']]
        fstate['p1_ddlSheng']['SelectedValueArray'] = [ddlSheng]
        fstate['p1_ddlShi']['F_Items'] = [[ddlShi, ddlShi, 1, '', '']]
        fstate['p1_ddlShi']['SelectedValueArray'] = [ddlShi]
        fstate['p1_ddlXian']['F_Items'] = [[ddlXian, ddlXian, 1, '', '']]
        fstate['p1_ddlXian']['SelectedValueArray'] = [ddlXian]
        fstate['p1_XiangXDZ']['Text'] = XiangXDZ
        fstate['p1_ShiFZJ']['SelectedValue'] = ShiFZJ
        fstate_json = json.dumps(fstate, ensure_ascii=False)
        fstate_bytes = fstate_json.encode("utf-8")
    except:
        print("----缺少必要文件“fstate_origin.json”或文件损坏,请检查当前目录\n")
        raise
    else:
        return base64.b64encode(fstate_bytes).decode()