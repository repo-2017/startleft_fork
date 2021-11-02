import logging

import requests

from startleft.apiclient.base_api_client import BaseApiClient

logger = logging.getLogger(__name__)


class UpdateProject(BaseApiClient):

    def do_call(self, project_id: int, otm_file):
        logger.debug("Updating project")

        url = self.irius_beta_url(f"/project/import/otm/{project_id}")
        headers = self.headers()
        files = self.open_file(otm_file)

        response = requests.put(url, headers=headers, files=files)
        self.check_response(response)
        response.close()
