from alirequest import *


request = req()
opsets= ["1"]
ops = ["2"]

op_data = [(1, 1), (1, 2), (2, 1), (2, 2)]

if True:
    print ('iteration start')

    # get new labels
    for op in op_data:
        request.get(op[0], op[1])

    # run training
    exec(open("/mnt/g27prist/TCO/TCO-Studenten/wagnerame/CRC_Komplexpraktikum/Network/pseudo_active_labeling.py").read())

    # upload results
    request.post("variances/variances.csv")
