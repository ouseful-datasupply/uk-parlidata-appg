import requests
from lxml import etree
from urllib.parse import urljoin
from pandas import DataFrame, read_html, concat

from bs4 import BeautifulSoup
import re

from tqdm import tqdm

def _getLinksFromPage(url, textcrib=None, hrefcrib=True):

    page = requests.get(url)

    #The file we have grabbed in this case is a web page - that is, an HTML file
    #We can get the content of the page and parse it
    soup=BeautifulSoup(page.content, "html5lib")
    #BeautifulSoup has a routine - find_all() - that will find all the HTML tags of a particular sort
    #Links are represented in HTML pages in the form <a href="http//example.com/page.html">link text</a>
    #Grab all the <a> (anchor) tags...
    
    if textcrib:
        souplinks=soup.find_all('a', text=re.compile(textcrib))
    elif hrefcrib:
        souplinks=soup.find_all('a', href=re.compile(hrefcrib))
    else:
        souplinks=soup.find_all('a')
    return souplinks

def _get_most_recent_APPG_link(url=None):
    if url is None:
        url='http://www.parliament.uk/mps-lords-and-offices/standards-and-financial-interests/parliamentary-commissioner-for-standards/registers-of-interests/register-of-all-party-party-parliamentary-groups/'

    links = _getLinksFromPage(url,textcrib='Registers published')

    #get the most recent link
    recent = sorted([link.text for link in links])[-1]
    link = [link for link in links if link.text == recent][0]

    url='http://www.parliament.uk'+link['href']
    links = _getLinksFromPage(url,hrefcrib='pa/cm/cmallparty.*htm')
    return links[0]

def getDetails(dfs,gid):
    df=dfs[0][:]
    df.set_index(0,inplace=True)
    df=df.T
    df['gid']=gid
    return df.reset_index(drop=True)
    
def getOfficers(dfs, gid):
    df=dfs[1][:]
    df.columns=['Property','Name', 'Party']
    df.set_index('Property',inplace=True)
    df=df[2:]
    df['gid']=gid
    return df.reset_index(drop=True)
    
def getContacts(dfs,gid):
    df=dfs[2][:]
    df.rename(columns=df[0], inplace=True)
    df['gid']=gid
    return df[1:].reset_index(drop=True)
    
def getAGM(dfs,gid):
    df=dfs[3].loc[:]
    df['gid']=gid
    return df.pivot(index='gid',columns=0,values=1).reset_index()
    
def getRegBenefits(dfs,gid):
    df=dfs[4][:]
    df.rename(columns=df.iloc[0], inplace=True)
    df['gid']=gid
    if len(df)>2:
        df.columns=['Source', 'Value', 'Received', 'Registered', 'gid']
    return df[3:]

def getInKindBenefits(dfs,gid):
    if len(dfs)>5:
        df=dfs[5][:]
        df.rename(columns=df.iloc[1], inplace=True)
        df=df[2:]
        df['gid']=gid
    else: return DataFrame()
    return df

def scraper(url=None, conn=None, exists=None, to_csv=False):
    if not url:
        a =  _get_most_recent_APPG_link()
        print('Using most recent file I can find: {}'.format(a.text))
        url = a['href']
        #url="https://www.publications.parliament.uk/pa/cm/cmallparty/170502/contents.htm"

    df_details=DataFrame() #getDetails(dfs,gid)
    df_officers=DataFrame() #getOfficers
    df_contacts=DataFrame() #getContacts(dfs,gid)
    df_AGM=DataFrame() #getAGM(dfs,gid)
    df_regBenefits=DataFrame() #getRegBenefits(dfs,gid)
    df_inKindBenefits=DataFrame() #getInKindBenefits(dfs,gid)
    
    doc = etree.HTML(requests.get(url).text)
    
    #Should really update db / annotate CSV after each load
    #Or group them and batch load every 20 or so
    for x in tqdm(doc.xpath('//*[@id="mainTextBlock"]/ul/li/a')):#doc.xpath('//p[@class="contentsLink"]/a'):
        #print(x.text, x.attrib['href'])
        #Use slug as gid
        gid=x.attrib['href'].split('.')[0]
        urlpath = '/'.join(url.split('/')[:-1])
        r = requests.get('/'.join([urlpath, x.attrib['href']]))
        gid= x.attrib['href'].replace('.htm','')
        dfs=read_html(r.text)
        df_details=concat([df_details,getDetails(dfs,gid)])
        df_officers=concat([df_officers,getOfficers(dfs,gid)]) #getOfficers
        df_contacts=concat([df_contacts,getContacts(dfs,gid)]) #getContacts(dfs,gid)
        df_AGM=concat([df_AGM,getAGM(dfs,gid)]) #getAGM(dfs,gid)
        df_regBenefits=concat([df_regBenefits,getRegBenefits(dfs,gid)]) #getRegBenefits(dfs,gid)
        df_inKindBenefits=concat([df_inKindBenefits,getInKindBenefits(dfs,gid)])
        
    if to_csv:
        df_details.to_csv('df_details.csv',index=False)
        df_officers.to_csv('df_officers.csv',index=False)
        df_contacts.to_csv('df_contacts.csv',index=False)
        df_AGM.to_csv('df_AGM.csv',index=False)
        df_regBenefits.to_csv('df_regBenefits.csv',index=False)
        df_inKindBenefits.to_csv('df_inKindBenefits.csv',index=False)
        
    if conn:
        df_details.to_sql(con=conn, name='df_details',if_exists=exists, index=False)
        df_officers.to_sql(con=conn, name='df_officers',if_exists=exists, index=False)
        df_contacts.to_sql(con=conn, name='df_contacts',if_exists=exists, index=False)
        df_AGM.to_sql(con=conn, name='df_AGM',if_exists=exists, index=False)
        df_regBenefits.to_sql(con=conn, name='df_regBenefits',if_exists=exists, index=False)
        df_inKindBenefits.to_sql(con=conn, name='df_inKindBenefits',if_exists=exists, index=False)
     
    return df_details, df_officers, df_contacts, df_AGM, df_regBenefits, df_inKindBenefits
           
