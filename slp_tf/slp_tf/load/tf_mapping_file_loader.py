import logging

from slp_base.slp_base.mapping_file_loader import MappingFileLoader

logger = logging.getLogger(__name__)


class TerraformMappingFileLoader(MappingFileLoader):

    def __init__(self, mapping_files: [bytes]):
        super(TerraformMappingFileLoader, self).__init__(mapping_files)

