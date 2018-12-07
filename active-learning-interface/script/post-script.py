import requests



url = 'http://localhost:8000/image/upload'
files = {'file': open('file.csv', 'rb')}

url_login='http://localhost:8000/admin/login/'

user='admin'
password='admin'

client = requests.session()
client.get(url_login)
csrftoken = client.cookies['csrftoken']
login_data = {'username':user,'password':password, 'csrfmiddlewaretoken':csrftoken, 'next': '/image/'}
r1=client.post(url_login,data=login_data)
csrftoken = client.cookies['csrftoken']
payload={'csrfmiddlewaretoken':csrftoken}
r = client.post(url, files=files, data=payload)
print(r.text)
