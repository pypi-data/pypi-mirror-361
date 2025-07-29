
import argparse

import pandas as pd
from dough.rag.retriever import LoadableRetriever

def main():
    """Loads data from a CSV file into a specified collection..

    This script uses argparse to accept command line arguments for specifying the CSV file, collection name, and vector field.
    It then reads the CSV file using pandas and inserts the data into the specified collection using the LoadableRetriever class.

    Example:
        Run the script from the command line using:
        python3 load.py --file input.csv --collection_name tskim_sql --vector_field question

    Note:
        - The CSV file must exist and be formatted correctly.
        - The collection_name and vector_field must be specified according to the requirements of the LoadableRetriever class
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", required=True, help="CSV file to load")
    ap.add_argument("-c", "--collection_name", required=True, help="Name of the collection to load data into")
    ap.add_argument("-v", "--vector_field", required=True, help="The vector field in the collection to target")
    args = ap.parse_args()

    loader = LoadableRetriever(args.collection_name)
    loader.insert(pd.read_csv(args.file), args.vector_field)

if __name__ == "__main__":
    main()

