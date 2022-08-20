from cookie import get_asp_net_sessionid,get_cas_page,get_location,get_ncov2019selfreport_shnu,get_viewstate,post_report
from local import get_time,get_config,generate_js,generate_fstate
import time

VERSION="1.0"

if __name__ == '__main__':
    print("  --------------------------------")
    print("  | 上海师范大学健康之路日报打卡 |")
    print("  |      SHNU_health_tool        |")
    print("  --------------------------------")
    print("                              "+VERSION+"\n")
    while True:
        try:
            username,password,ShiFSH,ShiFZX,ddlSheng,ddlShi,ddlXian,XiangXDZ,ShiFZJ=get_config()
            ctx=generate_js('des.js') #加密程序des.js在CAS的响应中
            BaoSRQ=get_time()
            fstate=generate_fstate(BaoSRQ, ShiFSH, ShiFZX, ddlSheng, ddlShi, ddlXian, XiangXDZ, ShiFZJ)
            asp_net_sessionid=get_asp_net_sessionid()
            jessionid,lt,execution=get_cas_page()
            location=get_location(jessionid,ctx,username,password,lt,execution)
            ncov2019selfreport_shnu=get_ncov2019selfreport_shnu(location,asp_net_sessionid)
            viewstate=get_viewstate(asp_net_sessionid,ncov2019selfreport_shnu,BaoSRQ)
            post_report(asp_net_sessionid,ncov2019selfreport_shnu,viewstate,BaoSRQ,ShiFSH,ShiFZX,ddlSheng,ddlShi,ddlXian,XiangXDZ,ShiFZJ,fstate)
        except:
            print("  --------------------------------")
            print("  |           打卡失败           |")
            print("  --------------------------------")
            print("            5秒后自动重试")
            time.sleep(5)
        else:
            print("  --------------------------------")
            print("  |           打卡成功！         |")
            print('  |          '+BaoSRQ+'          |')
            print("  --------------------------------")
            print("            5秒后自动退出")
            time.sleep(5)
            break