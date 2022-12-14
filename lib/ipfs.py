import requests
from fastapi import HTTPException
from models.settings import   Settings

settings = Settings()


def upload_to_ipfs(file):
    try:
        project_id = settings.infura_project_id
        project_secret = settings.infura_project_secret

        response = requests.post(
            '{0}/api/v0/add'.format(settings.ipfs_node_url), files={'fileOne': file}, auth=(project_id, project_secret))

    except Exception as e:
        print('\n\nIPFS ERROR: ',  e, '\n\n')
        raise HTTPException(
            status_code=500, detail="Unable to save file ")

    else:

        if not response.ok:
            print("IPFS ERROR: ", response.status_code, response.text)

            raise HTTPException(
                status_code=500, detail="Unable to save file ")

        result = response.json()

        return {

            'url': '{0}/{1}'.format(settings.ipfs_read_node, result['Hash']), 'cid': result['Hash']

        }