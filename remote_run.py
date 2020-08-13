

"""Script which runs remote spiders one by one  using scrapinhhgub Api

https://python-scrapinghub.readthedocs.io/en/latest/

"""
import os
import sys
from datetime import datetime
import json
from glob import glob

from keys import apikey  # insert your api key in keys.py
import logging
import shutil
from scrapinghub import ScrapinghubClient
from time import sleep

logging.basicConfig(level='DEBUG')
logger = logging.getLogger('Spider')


def run_spiders(ids: list, project):
    """Run spiders"""

    for id in ids:
        project.jobs.run(id)

        # check spider state

        try:
            # need time to initialize project.jobs.list otherwise sometimes an error occurs
            sleep(5)
            jobs_summary = project.jobs.list(state='running')
            key = jobs_summary[0].get('key', None)

        except Exception as e:
            logger.critical(f'{e} Restart script')
            raise SystemExit

        while True:
            jobs_summary_finished = project.jobs.list(state='finished')
            if not jobs_summary_finished or key != jobs_summary_finished[0]['key']:
                sleep(90)
            else:
                break
        store_data(key, id, project)


def store_data(key: str, id: str, project):
    """Store data"""
    data = []
    job = project.jobs.get(key)
    for item in job.items.iter():
        # delete useless key
        item.pop('_type', None)
        # clear data
        item = {key: value.encode('ascii', errors='ignore').decode('ascii') for key, value in item.items()}
        data.append(item)

    # saving the received data
    filename = f'./output/{id}_' + datetime.today().strftime('%Y-%m-%d-%H:%M') + '.json'
    if data:
        with open(filename, 'w') as f:
            json.dump(data, f)


def summary_data(project, ids: list):
    """Get summary of last jobs. Jobs quantity always equal quantity spiders in current project"""
    jobs_summary = project.jobs.list(state='finished', count=len(ids))
    for spider in jobs_summary:
        logger.info(f"""
                        spider: {spider.get('spider', 'None')}
                        job_id: {spider.get('key', 'None')}
                        state: {spider.get('state', 'None')}
                        items: {spider.get('items', 'None')}
                        errors: {spider.get('errors', 'None')}
                        """)


def copy_output(filenames: list):
    """Copy files if not empty"""
    for file in filenames:
        # check file is not empty
        if not os.stat(os.path.join(sys.path[0] + '/output/', file)) == 0:
            # copy file
            shutil.copy2(os.path.join(f'{file}'), sys.path[0] + '/backup/')
    logger.info('file copied to backup')


def main():
    """Main function starts all processes"""
    client = ScrapinghubClient(apikey)  # if your API key here then remove "from keys import apikey" string above
    project = client.get_project('yuor_id')  # project ID grab from scrapinghub
    ids = [spider['id'] for spider in project.spiders.list()]  # ['inco', 'ingra', 'quintecdistribucion', 'tec']
    logger.info(f'{ids}')

    # run spiders and save data
    run_spiders(ids, project)
    # some additional information
    summary_data(project, ids)

    pattern = os.path.join(sys.path[0] + '/output/', '*.json')

    # fetch list all .json in output directory

    filenames = glob(pattern)
    # save data in backup directory
    copy_output(filenames)


if __name__ == '__main__':
    main()
