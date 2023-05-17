import pickle, os


print(("="*10)+"[SAVE FILES]"+("="*10))
for saveFile in (files := list(os.listdir('data/saves')) + ['Exit']):
    print(f"- {saveFile}")

file = input("Select a save file: ")
if file.lower() == 'exit':
    exit()

if file in files:
    print(f"Opening {file}")
else:
    print("Invalid save file")

with open(f"data/saves/{file}", 'rb') as f:
    data = pickle.load(f)

    while True:
        code = input(">> ")
        if code == 'exit':
            with open(f"data/saves/{file}", 'wb') as f:
                pickle.dump(data, f)
            exit()
        elif code == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
        try:
            globs, locs = {'data': data}, {}
            exec(f"a={code}", globs, locs)

            if locs.get('a') != None:
                print(str(locs.get('a'))[:1000] + f" ...(+{len(str(locs.get('a'))) - 1000:,})" if len(str(locs.get('a'))) > 1000 else "")
        except Exception as e:
            print(e)