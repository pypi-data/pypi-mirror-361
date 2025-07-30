# Copyright (c) 2025 M. Fairbanks
#
# This source code is licensed under the Apache License, Version 2.0, found in the
# LICENSE file in the root directory of this source tree.

import os

from .u_folder import *
from .u_type import *

import urllib3
# https://urllib3.readthedocs.io/en/latest/user-guide.html

from bs4 import BeautifulSoup
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

import ssl

class uWeb:

    @staticmethod
    def LoadUrlData (Url:str)->bytes:
        '''
        Loads an Url and returns Url content in bytes.

        Returns *False* on error.
        '''
        try:
            # http = urllib3.PoolManager()
            http = urllib3.PoolManager(cert_reqs = ssl.CERT_NONE)
            urllib3.disable_warnings()

            resp=http.request('GET',Url,headers={'User-Agent': 'Mozilla/5.0'})
            resp.close()
            if resp.status in [200,201]:
                return resp.data
        except:
            pass

        return False

    @staticmethod
    def SaveUrl2File (Url, FolderPath=None, FilePath=None, Overwrite=True):
        '''
        Saves Url data to a file.

        If **FilePath** is specified, saves to this file.

        Otherwise, save to **FolderPath** using the resource name.
        '''
        # specify one of the following combinations:
            # FilePath : save to specified file
            # FolderPath only: append with resource name
        # returns one of:
            # string: filepath to target file, when successful
            # None: overwrite is False and file exists
            # False: failure

        target = FilePath
        if target is None and FolderPath is not None:
            lurl = Url.split('/')
            if len(lurl)>0:
                target = os.path.join(FolderPath, lurl[len(lurl)-1])
                ix = target.find("?")
                if ix!=-1:
                    target=target[:ix]

        if target is None:
            return False

        if Overwrite==False and os.path.isfile(target):
            return None

        targetfolder = os.path.dirname(target)
        if uFolder.ConfirmFolder(targetfolder) is False:
            return False

        try:
            data = uWeb.LoadUrlData(Url)
            if data is False:
                return False # not found
            with open(target,'wb') as f:
                f.write(data)
        except:
            return False

        if os.path.isfile(target):
            return target
        
        return False

class uSoup:

    @staticmethod
    def LoadSoup(Url, Parser='html.parser')->BeautifulSoup:
        '''
        Create a **BeautifulSoup** object from an **Url**.
        '''
        data = uWeb.LoadUrlData(Url)
        if data is False:
            return False
        return BeautifulSoup(data, Parser)

    @staticmethod
    def FindImagesReferences(Soup:BeautifulSoup)->list:
        '''
        Returns a list of image urls extracted from **Soup** based on a-tag "href". 
        '''
        ret = []
        a_list = Soup.find_all('a')
        for a in a_list:
            if 'href' in a.attrs:
                href = a.attrs['href']
                if uSoup.IsImage(href):
                    ret.append(href)
        return ret

    @staticmethod
    def FindImagesSources(Soup:BeautifulSoup)->list:
        '''
        Returns a list of image urls extracted from **Soup** based on img-tag "src" and "data-src".
        '''
        ret = []
        a_list = Soup.find_all('img')
        for a in a_list:
            if 'data-src' in a.attrs:
                src = a.attrs['data-src']
                ret.append(src)
            elif 'src' in a.attrs:
                src = a.attrs['src']
                ret.append(src)
        return ret
    
    _img_ext = ['jpg', 'jpeg', 'jfif', 'png', 'apng', 'bmp', 'gif', 'webp', 'svg', 'avif']
    
    @classmethod
    def AddImageExt(cls, Ext:list|str):
        '''
        Add image extensions to the list of known image extensions.

        Ext can be a string, a list of strings, or a comma delimited string.
        '''
        lst = uType.ConvertToList(Ext)
        if isinstance(lst, list):
            lst = [ext.replace('.', '').replace('*', '') for ext in lst]

        cls._img_ext.extend(lst)

    @classmethod
    def IsImage (cls, Url):
        '''
        Returns True if the image extension is a known image extension.
        '''
        if Url.find("type=album") != -1:
            return True
        ext = os.path.splitext(Url)[1].lower().replace('.', '')
        if ext in cls._img_ext:
            return True
        return False

    @staticmethod
    def FindAllText (Soup:BeautifulSoup, Limit:bool=False)->list:
        '''
        Returns a string of text extracted from *Soup*.

        If **Limit** is *True*, text is only extracted from the first tag found with text contents.
        '''
        text = []
        for child in Soup.descendants:
            if isinstance(child, str):
                nas = ''.join(char for char in child if ord(char) < 128)
                if len(nas)>0:
                    if Limit is True:
                        return nas
                    text.append(nas)

        if len(text)>0:
            return text

        return None

    @staticmethod
    def FindText (Soup:BeautifulSoup)->str:
        '''
        Returns a string of text extracted from *Soup*, limited to the first tag found with text contents.
        '''
        return uSoup.FindAllText(Soup, Limit=True)

    @staticmethod
    def ReadTable (Soup:BeautifulSoup)->list:
        '''
        Reads table text into a grid (list of lists):
        '''
        grid = []
        lrow = Soup.find_all(name="tr")
        for r in lrow:
            row = []
            lcol = r.find_all(name="td")
            for c in lcol:
                row.append(uSoup.FindText(c))
            grid.append(row)

        return grid
