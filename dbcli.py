import os
import pickle

print(("="*10)+"[SAVE FILES]"+("="*10))
# := is the (walwrus, i think?) it allows you to assign a variable and do stuff with it
# in the same line
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
    data = pickle.load(f) # Load the python object from the file

    while True:
        code = input(">> ") # basically just runs the python interpreter but with the save loaded
        if code == 'exit':
            with open(f"data/saves/{file}", 'wb') as f: # Save the object
                pickle.dump(data, f)
            exit()
        elif code == 'clear': # clear the terminal
            os.system('cls' if os.name == 'nt' else 'clear')
        try: # Don't want to crash the whole program if you write a bad line
            globs, locs = {'data': data}, {}
            exec(f"a={code}", globs, locs) # Run whatever code with the given globals and locals,
                                           # set the response equal to 'a' so we can capture the response

            if locs.get('a') != None: # print up to one thousand characters of the response
                print(str(locs.get('a'))[:1000] + f" ...(+{len(str(locs.get('a'))) - 1000:,})" if len(str(locs.get('a'))) > 1000 else "")
        except Exception as e:
            print(e) # just print the error, really should be using traceback for better errors but
                     # to be honest i never even use this program