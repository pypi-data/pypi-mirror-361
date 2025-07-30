import importlib

from torrra.indexers import INDEXERS_MAP


def get_indexer(name: str):
    indexer_module_path = INDEXERS_MAP[name]
    return importlib.import_module(indexer_module_path).Indexer()
