#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 20 20:42:06 2019

@author: wambo
"""

import requests
import getpass
import re
import os
import shutil
from bs4 import BeautifulSoup

print("Establishing Connection")
session=requests.Session()
r=session.get("https://elearning2.uni-heidelberg.de/login/index.php")
print("Retrieving login token")
cookie1=r.headers["Set-Cookie"][:-8]
soup=BeautifulSoup(r.text, "html.parser")
token=soup.find(name="input", attrs={"name":"logintoken"})["value"]



user=input("Got login token\nEnter username: ")
pw=getpass.getpass("Enter password:")
login=session.post("https://elearning2.uni-heidelberg.de/login/index.php",
                    headers={'User-Agent': 'Mozilla/5.0'},
                    data={"username": user, 
                          "password": pw, 
                          "logintoken":token})

if "You are not logged in" in login.text:
    raise ConnectionError("Couldnt log in to Moodle")
else:
    print("\n\nSuccessfully logged in")
print("Retrieving Courses\n\n")
home=BeautifulSoup(login.text, "html.parser")
ul=set(filter(lambda x: x["title"]!="Datei",home.find_all(name="a", href=re.compile("view.php\?id="))))
hrefs=set([el["href"] for el in ul])
rqs=[session.get(href) for href in hrefs]
titles=map(lambda x: BeautifulSoup(x.text, "html.parser").find(name="title").string, rqs)
for i, x in enumerate(titles):
    print(i, x)
to_dl=input("Which courses to download (Type numbers separated by spaces)").split(" ")
to_dl=list(map(lambda x:int (x) , to_dl))
for i, rq in enumerate(rqs):
    if i in to_dl:
        bs=BeautifulSoup(rq.text, "html.parser")
        folder_name=str(bs.find(name="title").string)
        print("Downloading from",folder_name)
        try:
            print("Creating folder",folder_name)
            os.mkdir(folder_name)
        except FileExistsError:
            print("Directory",folder_name, "already exists")
        docs=set(bs.find_all(name="a", href=re.compile("/mod/resource/view.php")))
        for doc in docs:
            print("Downloading next file")
            res=session.get(doc["href"], stream=True)
            if res.status_code==200:
                print("Download successful, writing to",res.headers["content-disposition"][17:].strip('"'))
                with open(folder_name+"/"+res.headers["content-disposition"][17:].strip('"'), "wb") as f:
                    res.raw.decode_content = True
                    shutil.copyfileobj(res.raw,f)