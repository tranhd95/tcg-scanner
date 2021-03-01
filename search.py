import glob
import cv2
from pathlib import Path
import sys
import vptree
from PIL import Image
import imagehash
import pickle


class SearchEngine:
    def __init__(self, hash_size=16):
        self.hash_size = hash_size
        self.hash_dict = None

    def build_hash_dict(self, img_paths):
        print("Building hash dict...")
        hash_dict = {}
        for img_path in img_paths:
            path = Path(img_path)
            img = Image.open(img_path)
            hash_ = imagehash.dhash(img, self.hash_size)
            hash_dict[hash_] = path.name
        print("Done building hash dict.")
        self.hash_dict = hash_dict
        return hash_dict

    def save(self, target_file):
        with open(target_file, "wb") as file:
            pickle.dump(self, file)

    def load(source_file):
        with open(source_file, "rb") as file:
            return pickle.load(file)

    def search_from_file(self, img_path):
        return self.search(Image.open(img_path))

    def search(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        hash_ = imagehash.dhash(img_pil, self.hash_size)
        min_dist = sys.maxsize
        min_name = ""
        for dict_hash, img_name in self.hash_dict.items():
            if (dist := dict_hash - hash_) < min_dist:
                min_dist = dist
                print("hamming:", min_dist)
                min_name = img_name
        return min_name, min_dist


def load_search_engine(source_file):
    return SearchEngine.load(source_file)
