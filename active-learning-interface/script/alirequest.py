import requests
import sys
from pathlib import Path
import os

class req:
    def post(self, path):

        """
        if len(sys.argv) == 0:
            exit()
        path = sys.argv[1]
        """

        ### url, an die csv hochgeladen wird
        url = 'http://10.2.89.30:8000/upload'

        ### 'file.cs' Pfad zur Datei, die hochgeladen wird
        files = {'file': open(path, 'rb')}

        ### login with username 'network'
        os.environ['NO_PROXY'] = '10.2.89.30'
        url_login='http://10.2.89.30:8000/'#admin/login/'
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

        print(r)


    def get(self, opset, op):

        """
        if len(sys.argv) < 2:
            exit()
        opset = sys.argv[1]
        op = sys.argv[2]
        """

        ### url, an die csv hochgeladen wird
        url = 'http://10.2.89.30:8000/csv/' + str(opset) + '/' + str(op) + '/'

        ### 'file.cs' Pfad zur Datei, die hochgeladen wird
        os.environ['NO_PROXY'] = '10.2.89.30'
        path = Path('/mnt/g27prist/TCO/TCO-Studenten/wagnerame/CRC_Komplexpraktikum/Annotations') / str(opset) / str(op)
        path.mkdir(exist_ok=True, parents=True)
        file = open(str(path / 'Ins.csv'), 'wb')

        r = requests.get(url, allow_redirects=True)
        print(r)
        file.write(r.content)

        #print(r.text)
