# File variables
PYTHON_SCRIPT_1 = test1.py
PYTHON_SCRIPT_2 = test2.py

# Règle pour exécuter le programme Python
run_python_1:
	python $(PYTHON_SCRIPT_1)

run_python_2:
	python $(PYTHON_SCRIPT_2)

# Règle pour exécuter les deux programmes en même temps
make : run_python_1 run_python_2