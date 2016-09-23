
# coding: utf-8

# # Image Downloader

# In[132]:

import os
import socket
import ssl # SSLError
import sys
import zlib

get_ipython().magic('matplotlib inline')
import matplotlib.pyplot as plt
from IPython.display import display
from pyprind import ProgBar
import pandas as pd 

from pymongo import MongoClient

import requests # t SSLError
import urllib.request, urllib.error, urllib.parse
from urllib.parse import quote, unquote
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen, url2pathname


# In[133]:

# Checking we are in the correct directory
download_dir = 'imgs'
if not os.path.exists(download_dir):
    os.mkdir(download_dir)
os.listdir(download_dir)[:10]


# ## Load cvs file containing urls 

# Start by loading csv file into dataframe.  
# Make sure the image_urls file is in the current directory

# In[134]:

#Load URL List
df = pd.read_csv('test_images_urls.csv')
image_urls = pd.Series(df['image_url']).dropna()


# ## Filter out urls that are not images

# Filtering out all the lines that do not start by htt. 

# In[135]:

urls = image_urls[ image_urls.str.startswith("htt")]
print("Valid Urls starting with \"htt*\" " + str(len(urls)) + 
      " from a total of "+ str(len(df)) + " in csv file.\n") 
df.info()


# Removing duplicated links since they must images that are logos, advertisements or other kinds of images that do not insterest us. We arbitrarely choose links that are repeated more than 10 times.

# In[136]:

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
image_urls_counts = image_urls.value_counts()
line, = ax.plot(image_urls_counts .values, color='blue', lw=2)
ax.set_yscale('log')
ax.set_ylabel("Log of Number of times repeated")
ax.set_xscale('log')
ax.set_xlabel("Log of urls")
ax.set_title("Repeated links histogram")
plt.show()


# In[137]:

print()
print("- First 10 values data ploted above: ")
print("    " + str(image_urls_counts[:10].values))
print("- Unique links:", len(image_urls.dropna().unique())) 
print("- Links found at most 10 times, should be photo: ", 
      len(image_urls_counts [image_urls_counts<=10]))
print("- Links found at least 10 times such as ads, spacers, logos:",
      len(image_urls_counts [image_urls_counts>10]))


# In[138]:

#Remove Urls repeated more than 10 times
val_counts = urls.value_counts()
repetition_dict = {url:repeted for url,repeted in val_counts.iteritems()}
url_list = [url for url in urls if repetition_dict[url] <= 10]
urls = pd.Series(url_list)
print("Remaining urls after we remove urls repeated 10 times: ", len(urls))


# The cell below is optional in case we already have downloaded partialy the images under the directory "../images/img" and want to keep downloading it.

# In[139]:

# Optional cell, make sure the "../images/img" path exists
# Remove files already loaded
files =  os.listdir(download_dir)
down_urls =  list(map(unquote, files))
remaining = urls[~urls.isin(down_urls)] 
#print(urls.isin(down_urls).value_counts())
#remaining = pd.read_csv('test.csv') # testing with a couple of files
print("Files downloaded: " + str(len(down_urls)))
print("Remaining files to be downloaded: " + str(len(remaining)))
remaining = pd.Series(remaining)


# In[140]:

#Removing unvalid extensions
exts =  [os.path.splitext(p)[1] for p in remaining] #croping text before "."
exts =  [ext.split('?')[0]  for ext in exts] #truncating text after extension
exts =  [ext.split('&')[0]  for ext in exts] #truncating text after extension
exts =  [ext.split('%')[0]  for ext in exts] #truncating text after extension
valid = pd.Series(exts)
img_remaining = remaining[list(valid.isin(['.jpg', '.gif' ,'.png', '.jpeg','.JPG']))] # what we keep
print("Remaining after unvalid extensions removed :" + str(len(remaining)))


# In[141]:

img_remaining


# ##  Downloading images
# 

# In[142]:

# TODO: Download images with a minimum width or height
bar = ProgBar(len(remaining), monitor=True)
unfetchables = []
timeouts = []
urlerrors = []
large_names = []

for i, image_name in enumerate(remaining):
    bar.update(item_id = image_name, force_flush=True)
    img =  None
    try:
        img = urlopen(image_name, None, 0.5).read()
    except (URLError, requests.exceptions.SSLError, ssl.SSLError) as e:
        urlerrors.append((image_name,e))
        print("URLError:   ",e ,image_name)
        continue
    except socket.timeout as e:
        timeouts.append((image_name, e))
        print("Timed out!", e, image_name)
        continue
    except Exception as e:
        unfetchables.append((image_name, e))
        print("Unknow exception", e, image_name)
        continue
    filename = quote(image_name, safe="")
    if len(filename) > 250:
        large_names.append(filename)
        filename = 'L' + filename[:250]
        #print("Name too long"+filename)
    if img:
        f = open(os.path.join(download_dir,filename),'wb')
        f.write(img)
        f.close()
print("urlerros", len(urlerrors), "timeouts", len(timeouts), 
      "unfetchables", len(unfetchables), "large names", len(large_names))


# In[93]:

print(len(urlerrors), len(timeouts), len(unfetchables), len(large_names))


# In[94]:

len(remaining)


# # Scratch Pad

# In[95]:

# Discarting malformed Urls
df = pd.read_csv('test_images_urls.csv')
urls = df['image_url'].dropna()
malformed = urls[ urls.str.contains("img.youtube.com")]
malformed_urls =  urls[ urls.str.startswith("htt")]
print(df.shape, urls.shape, urls.unique().shape, malformed_urls.unique().shape)


# In[96]:

#Checking images height and width
import pandas as pd
d = pd.read_csv('test_images_urls.csv')
print(d.shape)
print("** width **")
print(d['image_width'].describe())
print("** height **")
print(d['image_height'].describe())
rows_with_width = [ r for r, v in enumerate(d['image_width'].notnull()) if v]
rows_with_height = [ r for r, v in enumerate(d['image_height'].notnull()) if v]
print("rows_with_width", len(rows_with_width))
print("rows_with_height", len(rows_with_height))
print("rows_with_height and rows_with_height",len(set(rows_with_width+rows_with_height)))


# ### Checking Extension Distrubition
# 

# In[97]:

d = pd.read_csv('test_images_urls.csv')
paths = [ urlparse(name).path for name in d['image_url'].dropna()]
exts =  [os.path.splitext(p)[1] for p in paths]
ext = pd.Series(exts, dtype='category')
ext.unique()
ext.value_counts()
#len(ext)


# ### Duplicate Name Handling 

# In[98]:

# unquoting image names
urls = df['image_url'].dropna()
files = [ f for f in os.listdir(download_dir)]
down_urls =  map(unquote, files)
remaining = urls[~urls.isin(down_urls)]
remaining.shape


# ### Handling urls to be valid filenames for the images

# In[79]:

#%ls 
#name = 'http://static01.nyt.com/images/2014/11/12/opinion/krugman-circular/krugman-circular-thumbLarge-v4.png'
name = 'http%3A%2F%2Fstatic01.nyt.com%2Fimages%2F2015%2F11%2F20%2Fus%2Fwhy-it-takes-two-years-for-syrian-refugees-to-apply-to-enter-the-united-states-1448050604249%2Fwhy-it-takes-two-years-for-syrian-refugees-to-apply-to-enter-the-united-states-1448050604249-master495-v5.png'
real_name = unquote(name)
url2 = url2pathname(name)
url_quote = quote(name, safe="")
print(url2)
print(url_quote)
#f = open('img/'+ url_quote, 'wb')
#f = open("img/test", 'wb')

import base64
a = real_name
b = zlib.compress(real_name.encode("utf-8"))
c = base64.urlsafe_b64encode(zlib.compress(real_name.encode("utf-8")))

a,b,c,len(a),len(b),len(c)
# crop_index = 255 - len(urlsafe_base64encode(zlib encode))) 
# name = quote_name(file_name)[crop_index:]+ safeseparator + encoded name

