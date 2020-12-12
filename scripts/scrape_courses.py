import re
import os
import os.path as osp
import requests
import json
import argparse
import hashlib
import pandas
from bs4 import BeautifulSoup

def load_page(site,page,cache_dir):
    url=site + page
    fname=hashlib.sha1(url.encode('utf-8')).hexdigest()
    full_fname=osp.join(cache_dir,fname)

    #contents=None
    if not osp.exists(full_fname):
     #   contents=open(full_fname,'r').read()
    #else:
        r=requests.get(url)
        contents=r.text
        with open(full_fname,'w')as fh:
            fh.write(contents)
    return full_fname
def get_courses(filename):
    courses=[]
    soup=BeautifulSoup(open(filename,'r'),'html.parser')
    
#grab the div with class=view-content
    div_con=soup.find('div','view-content')
    
    sib=div_con.div
    courses=[]
    while sib is not None:
        info=sib.div.a.contents[0]
        courses.append(info)
        sib=sib.next_sibling
        if sib == '\n':
            sib=sib.next_sibling
    new=[]
    for course in courses:
        if re.match(r'([A-Z]{4}\s\w+)\s((\w+\s){1,})\(([+-]?[0-9]*[.]?[0-9]+)\scredit(s|)\)$',course):
            l=course.split()
            new.append(' '.join(l[0:2])+','+' '.join(l[2:-2])+','+l[-2][1:])
    return new


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('-c',help='cache dir')
    parser.add_argument('page', help='page number',)

    args=parser.parse_args()

    cache_dir=args.c
    page_num=args.page
    
   # if type(page_num) != int:
   #     raise Exception("Input for page number should be an int.")
    
    site='https://www.mcgill.ca/study/2020-2021/courses/search?page='

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    filename=load_page(site,str(int(page_num)),cache_dir)
    print('CourseID,Course Name,# of credits')
    print('\n'.join(map(str,get_courses(filename))))

if __name__ == "__main__":
    main()
