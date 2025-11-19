# test_bug.py

print("Début du script")
x = 10
y = 2  # ou toute autre valeur non nulle
if y != 0:
    result = x / y
    
result = x / y  # BUG : ZeroDivisionError

print("Résultat :", result)