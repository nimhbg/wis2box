###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

import json
import logging
from pathlib import Path

from wis2box.storage import get_data
from wis2box.topic_hierarchy import validate_and_load

LOGGER = logging.getLogger(__name__)


class Handler:
    def __init__(self, filepath: str, topic_hierarchy: str = None):
        self.filepath = filepath
        self.plugin = None

        LOGGER.debug('Detecting file type')
        if isinstance(self.filepath, Path):
            LOGGER.debug('filepath is a Path object')
            self.filetype = self.filepath.suffix[1:]
            self.is_http = self.filepath.as_posix().startswith('http')
        else:
            LOGGER.debug('filepath is a string')
            self.filetype = self.filepath.split(".")[-1]
            self.is_http = self.filepath.startswith('http')

        if topic_hierarchy is not None:
            th = topic_hierarchy
            fuzzy = False
        else:
            th = self.filepath
            fuzzy = True

        try:
            self.topic_hierarchy, self.plugin = validate_and_load(
                th, self.filetype, fuzzy=fuzzy)
        except Exception as err:
            msg = f'Topic Hierarchy validation error: {err}'
            LOGGER.error(msg)
            raise ValueError(msg)

    def handle(self, notify=False) -> bool:
        try:
            if self.is_http:
                self.plugin.transform(get_data(self.filepath),
                                      filename=self.filepath.split('/')[-1])
            else:
                self.plugin.transform(self.filepath)

            self.plugin.publish(notify)
        except Exception as err:
            msg = f'file {self.filepath} failed to transform/publish: {err}'
            LOGGER.warning(msg)
            return False
        return True

    def publish(self, backend) -> bool:
        index_name = self.topic_hierarchy.dotpath
        if not self.startswith('http'):
            with Path(self.filepath).open() as fh1:
                geojson = json.load(fh1)
                backend.upsert_collection_items(index_name, [geojson])
        else:
            geojson = json.load(get_data(self.filepath))
            backend.upsert_collection_items(index_name, [geojson])
        return True
