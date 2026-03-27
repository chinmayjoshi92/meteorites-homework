# Meteorite Landings Analysis

A Python script that pulls data from [JSON DataSource](https://dmachek.github.io/meteorites-homework/meteorite_landings.json) and prints answers in console.

## Assumptions:
- The dataset is a JSON file and certain keys might be missing from each data chunk e.g. mass, year etc. In that case
  the data point will be ignored. (Will not be considered for mass and year calculation)
- Dataset might update in the future. So data caching is used to skip downloading unchanged dataset which saves time.

## Caching:
The size of dataset right now is < 1MB but consider following cases
 - if this grows in the future lets say > 10 MBs
 - there are multiple CI/CD builds download this file during every build
 - and if there is rate limiting to download this file
 - if we skip download then we might lose the latest info

So this script uses a middle ground, script only downloads when there is a change in dataset. To achieve this ETags are used to check the changes on server side and if no new changes skip download.

## Script Flow:
1. Check for previously downloaded JSON and its ETag in .cache folder
2. Send GET request to server with previous ETag
3. If there's new data, write it to .cache/meteorites.json and store the new ETag.
4. Read the cached file
5. Process the data and print answers in console for following questions
   - Count the total entries
   - Find the heaviest meteorite
   - Count year frequencies using a dictionary and pick the most common one

## Error Handling:
 - Server is down or request times out -> use cached data (exit if no cache exists)
 - HTTP request error (4xx, 5xx) -> log the error and exit
 - Source JSON corrupted -> log the error and exit

## Future scope:
  - CLI arguments to use custom dataset URL
  - Create a dockerfile so it runs in a container so no venv needed
  - Cron jobs to run script after set time in CI

## How to Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install requests
python3 solution.py
```