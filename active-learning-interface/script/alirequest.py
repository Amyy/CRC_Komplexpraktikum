import requests
import pathlib
import os

class req:
    def post(self, path):

        """
        if len(sys.argv) == 0:
            exit()
        path = sys.argv[1]
        """

        ### url, an die csv hochgeladen wird
        url = 'http://localhost:8000/image/upload'

        ### 'file.cs' Pfad zur Datei, die hochgeladen wird
        files = {'file': open(path, 'rb')}

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


    def get(self, opset, op):

        """
        if len(sys.argv) < 2:
            exit()
        opset = sys.argv[1]
        op = sys.argv[2]
        """

        print("Get", opset, op, "data")

        ### url, an die csv heruntergeladen wird
        url = 'http://localhost:8000/image/csv/' + str(opset) + '/' + str(op) + '/'

        ### Pfad zur Datei, die heruntergeladen wird
        path = pathlib.Path("../../Annotations/") / pathlib.Path(str(opset)) / pathlib.Path(str(op))

        #file = open('labels-' + str(opset) + '-' + str(op) + '.csv', 'wb')

        if not os.path.exists(str(path)):
            os.makedirs(str(path))

        file = open(str(path / pathlib.Path('Ins.csv')), 'wb')

        r = requests.get(url, allow_redirects=True)
        print(r)
        file.write(r.content)

        #print(r.text)
