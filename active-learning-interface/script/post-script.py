import requests


### url, an die csv hochgeladen wird
url = 'http://localhost:8000/image/upload'

### 'file.cs' Pfad zur Datei, die hochgeladen wird
files = {'file': open('annotation.csv', 'rb')}

### login with username 'network'
url_login='http://localhost:8000/admin/login/'
user='network'
password='upload88'
client = requests.session()
client.get(url_login)
csrftoken = client.cookies['csrftoken']
login_data = {'username':user,'password':password, 'csrfmiddlewaretoken':csrftoken, 'next': '/image/'}
r1=client.post(url_login,data=login_data)
csrftoken = client.cookies['csrftoken']
payload={'csrfmiddlewaretoken':csrftoken}

#send files
r = client.post(url, files=files, data=payload)

#print(r.text)
