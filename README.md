# CRC_Komplexpraktikum
super cool project

Projekt starten:
in CRC_Komplexpraktikum/active-learning-interface/script, continuous.py ausführen


Eventuell muss man folgende Änderungen vornehmen: 

	active-learning-interface/script/alirequest.py replace localhost with IP-address of a PC where the app should run
	active-learning-interface/script/continuous.py in op_data sollen die zu verwendeten opset/ops stehen


	paths ändern:
	Network/datasets.py  csv_path
	Network/pseudo_active_labeling.py sys.insert()
	active-learning-interface/script/alirequest.py path in get(opset,op) function
	active-learning-interface/script/continuous.py path to pseudo_active_labeling.py

