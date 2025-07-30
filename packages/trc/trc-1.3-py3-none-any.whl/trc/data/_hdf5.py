# data/hdf5.py
# -- Import packages --
import h5py, os

# -- read hdf5-file with images and labels for classification --
def _read_class_hdf5(path: str) -> tuple:
    if not os.path.exists(path):
        raise FileNotFoundError(f"HDF5 file not found at: {path}")
    with h5py.File(path, 'r') as hf:
        images = hf['images']
        labels = hf['labels'][:]
        return images, labels

# -- write hdf5-file with images and labels for classification --
def _write_class_hdf5(path: str, images: list, labels: list):
    with h5py.File(path, 'w') as hf:
        hf.create_dataset('images', data=images, compression='gzip')
        hf.create_dataset('labels', data=labels, dtype=h5py.string_dtype(encoding='utf-8'))