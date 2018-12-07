url = 'localhost:8000/upload'
files = {'file': open('file.csv', 'rb')}

r = requests.post(url, files=files)
r.text
