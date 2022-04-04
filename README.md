# data-prep-scripts
Sometimes datasets published on the GBIF Norway IPT require once-off formatting and restructuring, this repo is for the scripts used to do that

All original spreadsheets sent to GBIF Norway get uploaded to Zenoodo. 

`docker-compose build` and `docker-compose run --service-ports script_service` enters an interactive shell. To start jupyter server, run `j` command alias. In `python /srv/scripts/[dataset-folder]` to run data formatting, source files should be downloaded from Zenodo beforehand.


