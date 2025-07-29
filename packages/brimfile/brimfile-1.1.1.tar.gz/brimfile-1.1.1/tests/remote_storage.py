import zarr
filename = r'https://s3.embl.de/bls-app-test/test.bls.zarr'

store = zarr.storage.FsspecStore.from_url(url=filename, read_only=True)
print(f"listing supported: {store.supports_listing}")

root = zarr.open_group(store=store, mode='r')

root["Brillouin_data"] # the key 'Brillouin_data' can e found
print(f"keys: {list(root.keys())}") # but when listing the keys in the root an empty list is returned







import fsspec                    

fs = fsspec.filesystem('s3', anon=True, asynchronous=True,
                    client_kwargs={'endpoint_url': f"https://s3.embl.de"})

store = zarr.storage.FsspecStore(fs, path = 'bls-app-test/test.bls.zarr',
                                read_only=True)


print(f"listing supported: {store.supports_listing}")

root = zarr.open_group(store=store, mode='r')

print(f"keys: {list(root.keys())}") # Now the keys are listed correctly










import sys
import os

# Get the absolute path to the brimfile directory
brimfile_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))

# Add it to sys.path
sys.path.insert(0, brimfile_path)

from brimfile import File, StoreType, Data, Metadata

filename = r'https://s3.embl.de/bls-app-test/test.bls.zarr'

f = File(filename, store_type=StoreType.S3)

# check if the file is read only
f.is_read_only()

#list all the data groups in the file
data_groups = f.list_data_groups(retrieve_custom_name=True)

# get the first data group in the file
d = f.get_data()
# get the name of the data group
d.get_name()

# get the number of parameters which the spectra depend on
n_pars = d.get_num_parameters()

# get the metadata 
md = d.get_metadata()
all_metadata = md.all_to_dict()
print(all_metadata)