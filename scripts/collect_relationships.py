import os
import os.path as osp
import requests 
import json
import argparse
import hashlib
from bs4 import BeautifulSoup

def get_filename(url,cache_dir):
    fname=hashlib.sha1(url.encode('utf-8')).hexdigest()
    full_fname=osp.join(cache_dir,fname)

    contents=None
    if osp.exists(full_fname):
        #print('load from cache')
        contents=open(full_fname,'r').read()
    else:
        #print('load from source')
        r=requests.get(url)
        contents=r.text
        with open(full_fname,'w') as fh:
            fh.write(contents)
    return full_fname
def extract_relationships(fname,person_url):
    relationships=[]
    soup=BeautifulSoup(open(fname,'r'),'html.parser')

    #grab the h4 with class=ff-auto-status
    status_h4=soup.find('h4','ff-auto-status')

    #grab the next sibling
    try:
        key_div=status_h4.next_sibling
    except:
        raise Exception("Cannot find this person")
    #grab all the elements
    candidate_links=key_div.find_all('a')

    relationships.extend(extract_relationships_from_candidate_links(candidate_links,person_url))
    if len(relationships) > 1:
        raise Exception('too many relationships')

    rels_h4=soup.find('h4','ff-auto-relationships')
    try:
        sib=rels_h4.next_sibling
    except:
        raise Exception("Cannot find this person")
    while sib is not None and sib.name=='p':
        candidate_links=sib.find_all('a')
        sib=sib.next_sibling
        sib.find_all('a')

        relationships.extend(extract_relationships_from_candidate_links(candidate_links, person_url))
    new=[]
    for name in relationships:
        new.append(name.split('/dating/')[1])
    return new
def extract_relationships_from_candidate_links(candidate_links,person_url):
    relationships=[]
    for link in candidate_links:
        if 'href' not in link.attrs:
            continue
        href=link['href']

        if href.startswith('/dating') and href!=person_url:
            relationships.append(href)
    return relationships


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('-c', help='config json file')
    parser.add_argument('-o',help='output file')

    args=parser.parse_args()
    
    #print('1')
    #load the config file
    with open (args.c,'r') as config:
        cf=json.load(config)
    
    cache_dir=cf['cache_dir']
    target_list=cf['target_people']
    
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    #print('2')
    out={}
    for name in target_list:
        url='https://www.whosdatedwho.com/dating/'+name
        person_url='/dating/'+name
        fname=get_filename(url,cache_dir)
        out[name]=extract_relationships(fname,person_url)
    
    #print(out)
    
    with open(args.o,'w') as output:
        output.write(json.dumps(out,indent=4))

if __name__ =='__main__':
    main()
