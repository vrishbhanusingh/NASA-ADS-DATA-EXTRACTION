"""
Module that contains the command line app.
"""
import argparse
import os
import traceback
import time
from google.cloud import storage
from label_studio_sdk import Client
from data_collection2 import *


GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
LABEL_STUDIO_URL = os.environ["LABEL_STUDIO_URL"]


def set_cors_configuration():
    """Set a bucket's CORS policies configuration."""

    print("set_cors_configuration()")
    bucket_name = GCS_BUCKET_NAME

    # Initiate Storage client
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    bucket.cors = [
        {
            "origin": ["*"],
            "method": ["GET"],
            "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
            "maxAgeSeconds": 3600,
        }
    ]
    bucket.patch()

    print(f"Set CORS policies for bucket {bucket.name} is {bucket.cors}")
    return bucket


def view_bucket_metadata():
    """Prints out a bucket's metadata."""

    print("view_bucket_metadata()")
    bucket_name = GCS_BUCKET_NAME

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    print(f"ID: {bucket.id}")
    print(f"Name: {bucket.name}")
    print(f"Storage Class: {bucket.storage_class}")
    print(f"Location: {bucket.location}")
    print(f"Location Type: {bucket.location_type}")
    print(f"Cors: {bucket.cors}")
    print(f"Default Event Based Hold: {bucket.default_event_based_hold}")
    print(f"Default KMS Key Name: {bucket.default_kms_key_name}")
    print(f"Metageneration: {bucket.metageneration}")
    print(
        f"Public Access Prevention: {bucket.iam_configuration.public_access_prevention}"
    )
    print(f"Retention Effective Time: {bucket.retention_policy_effective_time}")
    print(f"Retention Period: {bucket.retention_period}")
    print(f"Retention Policy Locked: {bucket.retention_policy_locked}")
    print(f"Requester Pays: {bucket.requester_pays}")
    print(f"Self Link: {bucket.self_link}")
    print(f"Time Created: {bucket.time_created}")
    print(f"Versioning Enabled: {bucket.versioning_enabled}")
    print(f"Labels: {bucket.labels}")


def get_projects(api_key):
    print("get_projects")

    # Examples using SDK: https://labelstud.io/sdk/project.html#label_studio_sdk.project.Project
    label_studio_client = Client(url=LABEL_STUDIO_URL, api_key=api_key)
    label_studio_client.check_connection()

    projects = label_studio_client.get_projects()
    print(projects)
    for project in projects:
        print(project.id, project.title, project.description)

    project = label_studio_client.get_project(1)
    print(project)


def get_project_tasks(api_key):
    print("get_project_tasks")

    # Examples using SDK: https://labelstud.io/sdk/project.html#label_studio_sdk.project.Project
    label_studio_client = Client(url=LABEL_STUDIO_URL, api_key=api_key)
    label_studio_client.check_connection()

    projects = label_studio_client.get_projects()
    project_id = projects[0].id
    project = label_studio_client.get_project(project_id)
    print(project)
    # print(project.get_tasks())
    print("Number of tasks:", len(project.tasks))

    labeled_tasks = project.get_labeled_tasks()
    print("Number of labeled tasks:", len(labeled_tasks))
    for labeled_task in labeled_tasks:
        print("Annotations:", labeled_task["annotations"])

def extract_and_upload_data(args=None):
    uploader = GCSUploader(GCS_BUCKET_NAME)  # TODO: replace with your bucket name
    handler = DataHandler(args.api_token, args.max_rows, args.start, args.params, args.sort, args.subset, gcs_blob_rows = args.gcs_blob_rows)
    handler.fetch_and_update_dataframe(uploader, args.query)

def main(args=None):
    if args.extract:
        extract_and_upload_data(args)
    
    if args.cors:
        set_cors_configuration()

    if args.metadata:
        view_bucket_metadata()

    if args.projects or args.tasks:
        if args.key == "":
            parser.error("-k argument i required for API access to LABEL Studio")

    if args.projects:
        get_projects(args.key)

    if args.tasks:
        get_project_tasks(args.key)
        
    


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Data Labeling CLI")

    parser.add_argument(
        "-c",
        "--cors",
        action="store_true",
        help="Set the CORS configuration on a GCS bucket",
    )
    
    parser.add_argument(
        "-e",
        "--extract",
        action="store_true",
        help="extract data from nasa/ads and upload to a GCS bucket",
    )
    parser.add_argument(
        "-m",
        "--metadata",
        action="store_true",
        help="View the CORS configuration for a bucket",
    )
    parser.add_argument(
        "-p", "--projects", action="store_true", help="List projects in Label studio"
    )
    parser.add_argument(
        "-t", "--tasks", action="store_true", help="View tasks from a project"
    )
    parser.add_argument("-k", "--key", default="", help="Label Studio API Key")

    parser.add_argument('--api_token', default = 'Bde9txgkHsD5UDCAEV0hdDnk6mHJ2PD7ccyvT4G3',type=str, help='API token')
    
    parser.add_argument('--query', default ="year:2013-2023",type=str, help='Query')
    
    parser.add_argument('--max_rows', default = 1000000, type=int, help='Maximum number of rows')
    parser.add_argument('--gcs_blob_rows', default = 4000, type=int, help='Maximum number of rows')
    parser.add_argument('--start',default =0, type=int, help='Start')
    
    parser.add_argument('--params',default ="bibcode,id,author,title,year,doi,keyword,\
        abstract,classic_factor,citation_count,read_count,reference_count,reference,\
            readers,metrics", type=str, help='Parameters')
    
    parser.add_argument('--sort',default ="classic_factor desc", type=str, help='Sort')
    
    parser.add_argument('--subset',default ="database:astronomy", type=str, help='Subset')
    
    args = parser.parse_args()

    main(args)
