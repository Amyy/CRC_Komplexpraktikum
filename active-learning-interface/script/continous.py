from alirequest import *


request = req()
opsets= ["1"]
ops = ["2"]

op_data = [(1, 1), (1, 2), (2, 1), (2, 2)]

while True:

    # get new labels
    for op in op_data:
        request.get(op[0], op[1])

    # run training
    exec(open("./pseudo_active_labeling.py").read())

    # upload results
    request.post("variances.csv")