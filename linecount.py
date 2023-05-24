import os

linecount = 0
folders   = ['_types', 'cheats', 'components', 'data', 'enemies', 'game', 'tasks', 'util', 'viewports']
for folder in folders:
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), 'r') as f:
                    linecount += len(f.readlines())

print(f"Total lines of code: {linecount}")