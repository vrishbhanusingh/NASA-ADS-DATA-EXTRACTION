# SpaceScribe: Nasa/ads data collection and versioning
SpaceScribe is a targeted title generation project where we will be generating titles of academic papers to maximize readability based on the reads. 

Below you can see the model architecture and the flow of data.

#### Pretraining 
We first train a model to predict the read count from just the title. 
![image](https://hackmd.io/_uploads/H1VdoyqYT.png)
#### RL finetuning
We then use an llm to generate titles from the abstracts, use the pretrained regression model to predict reads for each of the generated title and then use this as 'reward' for RL fintuning
![image](https://hackmd.io/_uploads/HyWRskqF6.png)



This is the data collection repo for the space scribe project for AI-5. We will be extracting data from the NASA/ADS APIs and uploading to a GCS bucket. We will be developing infrastructure for RLHF fintuning through label studio and using DVC for data versioning. All of these components are different components. 

![image](https://hackmd.io/_uploads/r19oLg5F6.png)

The code seen here is mostly forked from the github repo of AI-5 lecture 6 tutorials about container networks and dataset versioning. 
## Usage
* Have Docker installed
* Cloned this repository to your local machine with a terminal up and running





## Setup GCP Credentials

### Create a local **secrets** folder


Your folder structure should look like this:
```
   |-data-extraction
   |-secrets
```

### Attach GCP Credentials to Container

- set the `GOOGLE_APPLICATION_CREDENTIALS` to `/secrets/data-service-account.json` in the docker compose file
- Make sure the `GCP_PROJECT` matches your GCP Project


### Create GCS Bucket
- Go to `https://console.cloud.google.com/storage/browser`
- Create a bucket
- Create a folder `metrics_api_data` inside the bucket
- Create a folder `search_api_data` inside the bucket
- Create a folder `rlhf_tuning_data` inside the bucket
- Create a folder `dvc_store` inside the bucket
![image](https://hackmd.io/_uploads/BkRLxl9Y6.png)

##### Run `docker-shell.sh` 

This will run two container. The label studio container and a CLI that will help you extract data from nasa/ads api.

#### Extraction and upload data
Run `python cli.py -e`

Refer to the python file for the arguments needed to be provided. 

## Data Versioning

### Fork the github repository
- Fork or download from [here](https://github.com/vrishbhanusingh/data-versioning)

Your folder structure should look like this:
```
   |-data-extraction
   |---docker-volumes
   |-----label-studio
   |-data-versioning
   |-secrets
```

- Run `sh docker-shell.sh`




### Version Data using DVC


#### Initialize Data Registry

`dvc init`

#### Add Remote Registry to GCS Bucket (For Data)
`dvc remote add -d dataset gs://ai5_nasa_ads_data/dvc_store`

#### Add the dataset to registry
`dvc add dataset`

#### Push Data to Remote Registry
`dvc push`

You can go to your GCS Bucket folder `dvc_store` to view the tracking files

It should look a little bit like this. 

![image](https://hackmd.io/_uploads/Bytf4g5YT.png)


#### Update Git to track DVC
- First run git status `git status`
- Add changes `git add .`
- Commit changes `git commit -m 'dataset updates...'`
- Add a dataset tag `git tag -a 'dataset_v1' -m 'tag dataset'`
- Push changes `git push --atomic origin main dataset_v1`


