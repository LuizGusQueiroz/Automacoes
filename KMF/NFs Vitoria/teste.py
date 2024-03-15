import os
files = [fr'notas\{file}' for file in os.listdir('notas')]
for file in files:
    os.remove(file)