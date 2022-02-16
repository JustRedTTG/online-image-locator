import math
import time

from github import Github

import bottle, os, psycopg2

def listDIR(where, only=False):
    stuff = os.listdir(where)
    if only:
        i = 0
        while i < len(stuff):
            if os.path.isdir(stuff[i]):
                i += 1
            else:
                del stuff[i]
                i = 0
    return stuff

from datetime import datetime
try:
    #DATABASE_URL = os.environ['DATABASE_URL']
    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
except:
    print('error')
    exit()
#conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn = None

APP = bottle.Bottle()
request = bottle.request
response = bottle.response
secret = "DWH2UW5WH"
debug = False
try:
    with conn.cursor() as cur:
        cur.execute("""create table if not exists data (
image BLOB,
format TEXT default '%x %y'
)""")
except:
    pass

try:
    if os.environ['debug'] == '1':
        debug = True
    pc_mode = False
except:
    debug = True
    pc_mode = True
try:
    os.chdir('/app/online image locator')
except:
    pass
def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def top():
    return ''
    cur = 1
    html = """
<div style="display: flex;">
    <div style="color: #40FF40; background: #40FF40; width: """+str(cur*100)+"""%; height: 10%;text-align: left;  padding-left: 1%;">a</div>
    <div style="color: #FFFFFF; background: #303030; width: """+str(100-cur*100)+"""%; height: 10%;text-align: right;padding-right: 1%;"><B>"""+mbf(USED)+""" / 500 MB</B></div>
</div>"""
    return html
def redirect(place=''):
    return """\
<!doctype HTML>
<html>
    <head>
        <meta http-equiv="refresh" content="0; URL='"""+place+"""'" />
    </head>    
</html>"""
def head(tit="School Resources"):
    return f'''<head><meta content="width=device-width, initial-scale=1" name="viewport" /><title>{tit}</title>
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="mask-icon" href="/safari-pinned-tab.svg" color="#63c094">
<meta name="msapplication-TileColor" content="#63c094">
<meta name="theme-color" content="#63c094">    
</head>'''
def header(before='',middle='',after=''):
    return """<header><div class="headerdiv">
    """+before+"""
    <form action="/" method="post">
        <button type="submit"><h id="scale2" class="shorty"><span></span></h></button>
    </form>
    """+middle+"""
    
    """+after+"""
</div></header>"""
def style():
    return """<style>
    .float {
        width: 200px;
        height: auto;
        text-align: center;
        margin-right: 5px;
        float: right;
        clear: both;
    }
    .float p {
        padding: 0px;
        margin: 0px;
        line-break: anywhere;
    }
    .float2 {
        width: 200px;
        height: auto;
        text-align: center;
        margin-right: 250px;
        float: right;
        clear: both;
    }
    .float2 p {
        padding: 0px;
        margin: 0px;
        line-break: anywhere;
    }
    .description {
        width: 180px;
        height: auto;
        margin-left: 10px;
    }
    .infobuttons {
        display: flex;
    }
    .classdiv img
    {
        width: 80%;
        margin: 0.2%;
        margin-right: 0px;
    }
    .classdiv
    {
        background: #09FFC5;
        display: flex;
        justify-content: left;
        align-items: center;
        height: auto;
        padding: 0px;
    }
    .classdiv .infodiv
    {
        background: #EEEEEE;
        padding: 0px;
        margin: 0px;
        width: 19.8%;
        word-wrap: break-word;
    }
    .headerdiv
    {
        display: flex;
        justify-content: left;
        align-items: center;
        padding: 0px;
        margin: 0px;
    }
    .headerdiv h3, a
    {
        padding:0px;
        margin:0px;
        width: 100% auto;
    }
    header
    {
        background: #404040;
        height: 10%;
        width: 100% auto;
        margin: 0px;
        padding-right: 10px;
        color: #09FFC5;
    }
    header button
    {
        padding: 10px;
    }
    header a
    {
        color: inherit;
    }
    html, body
    {
        background: #505050;
        padding: 0px;
        margin: 0px;
        font-family: Helvetica, sans-serif;
    }
    ul
    {
        color: #09FFC5;
    }
    button
    {
        border: none;
        text-decoration: none;
        /* CRISTMAS EGG */
        /* background: url("/other/btn_c.png"), url("https://redicons.free.bg/school-resources/btn_c.png"); */
        /* background-size: 64px 64px; */
        /* color: white; */
        /* text-shadow: -1px -1px 2px #FF0000, 1px -1px 2px #FF0000, -1px 1px 2px #FF0000, 1px 1px 2px #FF0000; */
        font-weight: bold;
        /* DEFAULT */
        background: #09FFC5;
        padding: 5px;
        margin: 2px;
    }
    button#waiting
    {
        /* background: url("/other/btn_c.png"), url("https://redicons.free.bg/school-resources/btn_c.png"); */
        background-size: 64px 64px;
    }
    .infobuttons
    {
        background: #A9FFC5;
        width: 75px;
        height: 30px;
    }
    .infodiv
    {
        background: #FFD0FF!important;
    }
    .classdiv #custom
    {
        background: #EEEEEE!important;
    }
    #new
    {
        background: #ff7926;
        color: #FFFFFF;
    }
    #old
    {
        background: #24c9c7;
        color: #FFFFFF;
    }
    #waiting
    {
        background: #f0de3e;
        color: #000000;    
    }
    #canceled
    {
        background: #ff3126;
    }
    #gone
    {
        background: #EEEEEE;
    }
    .shorty:after
    {
        content: 'School Resources';
    }
    @media only screen and (max-width: 768px)
    {
        .float
        {
            display: none;
        }
        .shorty:after
        {
            content: 'SR';
        }
        #scale2, #new, #old, #waiting, #canceled, #gone
        {
            font-size: 200%;
        }
        button
        {
            padding: 2px;
            margin: 1px;
        }
        .infodiv
        {
            float: down;
            width: 100% !important;
            font-size: 200%;
        }
        .classdiv
        {
            display: list-item;
            width: 100% 
        }
        img
        {
            width: 99.5% !important;
        }
        .infobuttons
        {
            width: 100px;
            height: 43px;
        }
        .infobuttons button
        {
            padding: 10px;
            margin: 4px;
        }
        
    }
</style>"""

@APP.get("/")
def index():
    html = "<!doctype html><html><body>" + top() + header() + style()
    html += head()
    html += """<ul>"""
    html += """</ul></body></html>"""
    return html
def run():
    #print("RUNNING SERVER")
    if os.path.exists('.git'):
        #print('reload or start')
        bottle.run(app=APP, reloader=True)
    else:
        print('running on heroku!')
        bottle.run(application=APP)

if __name__ == '__main__':
    run()