import math
import random
import bottle, os, psycopg2
import ftputil
import cv2
import imutils
listOfScales = [0.01, 0.06210526315789474, 0.11421052631578947, 0.16631578947368422, 0.21842105263157896, 0.2705263157894737, 0.32263157894736844, 0.37473684210526315, 0.4268421052631579, 0.4789473684210527, 0.5310526315789474, 0.5831578947368421, 0.6352631578947369, 0.6873684210526316, 0.7394736842105263, 0.791578947368421, 0.8436842105263158, 0.8957894736842106, 0.9478947368421053, 1.0]
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
try:
    DATABASE_URL = os.environ['DATABASE_URL']
    password = os.environ['password']
except:
    print('error')
    exit()
from datetime import datetime
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
def connectFTP():
    return ftputil.FTPHost("redlocate.free.bg","redlocate.free.bg",password)
#conn = None

APP = bottle.Bottle()
request = bottle.request
response = bottle.response
secret = "DWH2UW5WH"
debug = False
try:
    with conn.cursor() as cur:
        cur.execute("""create table if not exists data (
imageID TEXT ,
format TEXT default '%x %y'
)""")
    conn.commit()
except Exception as e:
    print("Couldn't make TABLE",e)

try:
    if os.environ['debug'] == '1':
        debug = True
    pc_mode = False
except:
    debug = True
    pc_mode = True
try:
    os.chdir('/app')
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
def head(tit="OIL~"):
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
        float: center;
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
        /* background: url("/other/btn_c.png"), url("https://redicons.free.bg/locateimg/btn_c.png"); */
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
        /* background: url("/other/btn_c.png"), url("https://redicons.free.bg/locateimg/btn_c.png"); */
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
        content: 'Online Image Locatior';
    }
    @media only screen and (max-width: 768px)
    {
        .float
        {
            display: none;
        }
        .shorty:after
        {
            content: 'OIL~';
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
def id_db(id):
    with conn.cursor() as cur:
        cur.execute(f"""SELECT imageID from data
where imageID = '{id}'""")
        length = len(cur.fetchall())
        return length == 0
@APP.get("/<favicon>")
def icon(favicon):
    if os.path.exists(f'favicon/{favicon}'):
        return bottle.static_file(root="favicon/", filename=favicon)
    else:
        response.status = 404
        return '404 no such favicon file'
@APP.post("/locate/<location>")
def findIT(location):
    image = request.files.get('image')
    if image:
        with conn.cursor() as cur:
            cur.execute(f"""SELECT format from data
where imageID = '{location}'""")
            format = cur.fetchone()[0]
        x = 0
        y = 0
        if os.path.exists(f'temp/{location}.png'):
            os.remove(f'temp/{location}.png')
        if os.path.exists(f'temp/{location}_locator.png'):
            os.remove(f'temp/{location}_locator.png')
        with connectFTP() as ftp:
            ftp.download(f'{location}.png',f'temp/{location}.png')
        image.save(f'temp/{location}_locator.png')

        img = cv2.imread(f'temp/{location}_locator.png')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(f'temp/{location}.png', 0)
        best_match = None
        for scale in listOfScales:
            resized_template = imutils.resize(template, width=int(template.shape[1] * scale))
            res = cv2.matchTemplate(img, resized_template, cv2.TM_SQDIFF)
            min_val, _, min_loc, _ = cv2.minMaxLoc(res)
            if best_match is None or min_val <= best_match[0]:
                ideal_scale = scale
                h, w = resized_template.shape[::]
                best_match = [min_val, min_loc, ideal_scale]
        top_left = best_match[1]
        x = top_left[0] + w/2
        y = top_left[1] + h/2
        if os.path.exists(f'temp/{location}.png'):
            os.remove(f'temp/{location}.png')
        if os.path.exists(f'temp/{location}_locator.png'):
            os.remove(f'temp/{location}_locator.png')
        return format.replace('%x',str(x)).replace('%y',str(y))
    return 'please try again, image=@LOCATION'
@APP.get("/locate/<location>")
def locate(location):
    return f"""<h1>Sorry, please use post method.</h1>
<h3>This is the image you tried to access BTW!</h3>
<img src="https://redlocate.free.bg/{location}.png">
<h4>HINT: If you see nothing, opps, you got the ID wrong!!!</h4>
<form action="/locate/{location}" method="post">
<input type="file" name="image">
<input type="submit" value="Locate!">
</form>"""
@APP.post("/")
def postIndex():
    return redirect('/')
@APP.post("/c/")
def create():
    identifier = request.forms.get("identifier")
    image = request.files.get("image")
    id = random.randint(0,1000000000000)
    while not id_db(id):
        id = random.randint(0, 1000000000000)
    image.save(f"temp/{id}.png")
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO data
VALUES ('{id}', '{identifier}');""")
        with connectFTP() as ftp:
            ftp.upload(f"temp/{id}.png", f'{id}.png')
        os.remove(f"temp/{id}.png")
        conn.commit()
    return f"""<h1>GREAT!</h1>
<h3>Go brag to your friends. you have the id of {id}</h3><br>
<ul>
<h2>{identifier}</h2>
<img src="">
</ul>"""
@APP.get("/")
def index():
    html = "<!doctype html><html><body>" + top() + header() + style()
    html += head()
    html += """<div style="margin-left:40%;"><form action="c/" method="post" enctype="multipart/form-data">
    <input type="text" name="identifier" value="%x %y"><br>
    <input type="file" name="image"><br>
    <input type="submit" value="Create Locator" style="text-align:center;"><br>
    </form></div>"""
    html += """</body></html>"""
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