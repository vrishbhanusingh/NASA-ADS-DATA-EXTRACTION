import os
import argparse
import pandas as pd
from google.cloud import storage
import requests
from urllib.parse import urlencode
# import dask.dataframe as dd
# import pyarrow as pa 

class GCSUploader:
    def __init__(self, bucket_name):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)

    def upload_blob(self, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {destination_blob_name}.")

class DataHandler:
    def __init__(self, api_token, max_rows, start, params=None, sort=None, subset=None, gcs_blob_rows = None):
        self.api_token = api_token
        self.max_rows = max_rows
        self.start = start
        self.params = params
        self.sort = sort
        self.subset = subset
        self.gcs_blob_rows = gcs_blob_rows
        # self.schema = {'bibcode': pa.string(),
        #                'abstract': pa.string(),
        #                'author': pa.list_(pa.string()),
        #                'doi': pa.list_(pa.string()),
        #                'id': pa.string(),
        #                'keyword': pa.list_(pa.string()),
        #                'title': pa.list_(pa.string()),
        #                'year': pa.string(),
        #                'read_count': pa.int64(),
        #                'classic_factor': pa.int64(),
        #                'reference': pa.list_(pa.string()),
        #                'citation_count': pa.int64(),
        #                'arXiv_PDF_Link': pa.string(),
        #                '__null_dask_index__': pa.int64()}

    def fetch_data(self, query, start=0, rows=2000, params=None, sort=None, subset=None, **kwargs):
        # API query
        encoded_query = urlencode({
            "q": query,
            "fl": params,
            "rows": rows,
            "start": start,
            "sort": sort,
            "fq": subset
        })

        # API request
        results = requests.get(f"https://api.adsabs.harvard.edu/v1/search/query?{encoded_query}",
                               headers={'Authorization': 'Bearer ' + self.api_token})

        # Extract relevant information
        try:
          docs = results.json()['response']['docs']
        except:
          docs = None

        return docs

    def fetch_and_update_dataframe(self, uploader, query):
        chunk_size = 2000
        dataframe = pd.DataFrame()
        n_extract = 0 

        while len(dataframe) < self.max_rows:
            # Fetch data
            docs = self.fetch_data(query, start=self.start, rows=chunk_size, params=self.params, sort=self.sort, subset=self.subset)

            # Update the DataFrame
            dataframe = pd.concat([dataframe, pd.DataFrame(docs)], ignore_index=True)

            # Increment start for the next API call
            self.start += chunk_size
            n_extract += chunk_size
            print(n_extract, " files extracted")
    

            if n_extract % self.gcs_blob_rows == 0:
                try:
                    dataframe['arXiv_PDF_Link'] = dataframe['bibcode'].apply(lambda x: f"https://ui.adsabs.harvard.edu/link_gateway/{x}/EPRINT_PDF")
                except:
                    dataframe['arXiv_PDF_Link'] = None

                file_name = f"data_chunk_{n_extract//self.gcs_blob_rows}.csv"
                # ddf = dd.from_pandas(dataframe, npartitions = 20)
                # ddf.to_parquet(file_name, schema = self.schema)
                # ddf.to_parquet(f'gs://{uploader.bucket}/search_api_data/{file_name}', schema = self.schema)
                dataframe.to_csv(file_name, index=False)
                uploader.upload_blob(file_name, "search_api_data/" + file_name)  # TODO: replace with your desired object name in GCS
                print(file_name, ' uploaded successfully')
                
                dataframe = pd.DataFrame()
            # Break the loop if the maximum number of rows is reached
            
            
            if len(dataframe) >= self.max_rows:
                break
            
        return dataframe


