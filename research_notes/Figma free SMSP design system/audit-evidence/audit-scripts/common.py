import re, json, os, sys, glob
def load(project):
    files={}
    for p in sorted(glob.glob(os.path.join(project,'*.dc.html'))):
        files[os.path.basename(p)]=open(p,encoding='utf-8',errors='replace').read()
    canvas=json.load(open(os.path.join(project,'canvas.json')))
    return files,canvas
RE_HELMET=re.compile(r'<helmet>(.*?)</helmet>',re.S)
RE_SCRIPT=re.compile(r'<script type="text/x-dc"[^>]*>(.*?)</script>',re.S)
RE_CSSCOMMENT=re.compile(r'/\*.*?\*/',re.S)
RE_HTMLCOMMENT=re.compile(r'<!--.*?-->',re.S)
def split(src):
    """returns helmet, markup (x-dc minus helmet), script"""
    hel='\n'.join(RE_HELMET.findall(src))
    scr='\n'.join(RE_SCRIPT.findall(src))
    m=re.search(r'<x-dc>(.*)</x-dc>',src,re.S)
    body=m.group(1) if m else src
    body=RE_HELMET.sub('',body)
    return hel,body,scr
def decomment(src):
    s=RE_CSSCOMMENT.sub('',src)
    s=RE_HTMLCOMMENT.sub('',s)
    return s
