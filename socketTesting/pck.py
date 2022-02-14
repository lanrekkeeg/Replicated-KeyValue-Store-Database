import pickle

'''
# define a list of places
placesList = ['Berlin', 'Cape Town', 'Sydney', 'Moscow']

with open('listfile.data', 'wb') as filehandle:
    # store the data as binary data stream
    pickle.dump(placesList, filehandle)
    


# load additional module

with open('listfile.data', 'rb') as filehandle:
    # read the data as binary data stream
    placesList = pickle.load(filehandle)
    

print(placesList)

# define a list of places
placesList = ['Berlin', 'Cape Town', 'Sydney']

with open('listfile.data', 'wb') as filehandle:
    # store the data as binary data stream
    pickle.dump(placesList, filehandle)
    
    
with open('listfile.data', 'rb') as filehandle:
    # read the data as binary data stream
    placesList = pickle.load(filehandle)
    
print(placesList)
'''
with open('hld.data', 'rb') as filehandle:
    # read the data as binary data stream
    placesList = pickle.load(filehandle)
    
print(placesList)