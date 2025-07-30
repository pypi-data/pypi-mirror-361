import json
import logging
import os
import shutil
from typing import List

from ptools_base.schema import AssertSchema, EnvSchema

logger = logging.getLogger(__name__)

ASSERT_PATH_KEY = 'ASSERT_PATH_KEY'
EXTRA_PATH_KEY = 'EXTRA_PATH_KEY'
ENV_PATH_KEY = 'ENV_PATH_KEY'


def write_asserts(data: List[AssertSchema]):
    """
    write asserts data
    since: v1.1.x
    :param data: asserts data
    """
    assert_path = os.environ.get(ASSERT_PATH_KEY)
    print(f"reading ASSERT_PATH_KEY: {assert_path} from env")
    if assert_path:
        # create if file not exist
        if not os.path.exists(assert_path):
            with open(assert_path, 'w', encoding="utf-8"):
                pass
        existing_data = []
        # load old data
        with open(assert_path, 'r', encoding="utf-8") as file:
            if os.path.getsize(assert_path) > 0:
                file.seek(0)
                existing_data = json.load(file)

        # combine and write
        with open(assert_path, 'w', encoding="utf-8") as file:
            combined_data = existing_data + [i.model_dump() for i in data]
            file.seek(0)
            file.truncate()
            json.dump(combined_data, file, ensure_ascii=False)
    else:
        print("no ASSERT_PATH_KEY found")


def copy_2_extra(src: str):
    """
    copy source to extra path, for extra upload
    since: v1.1.x
    :param src: source path, a file or directory
    :return extra path or False
    """
    extra_path = os.environ.get(EXTRA_PATH_KEY)
    print(f"reading EXTRA_PATH_KEY: {extra_path} from env")
    if extra_path:
        if os.path.exists(src):
            if os.path.isdir(src):
                print(f"copying dir {src} to extra path: {extra_path}")
                return shutil.copytree(src, os.path.join(extra_path, src))
            else:
                print(f"copying file {src} to extra path: {extra_path}")
                return shutil.copy(src, extra_path)
        else:
            logger.warning(f"no extra path found: {src}")
            return False
    else:
        print("no EXTRA_PATH_KEY found")


def write_envs(env_schemas: List[EnvSchema]):
    """
    write env data to env_file
    since: v1.5.x
    :param env_schemas: env data
    """
    env_path = os.environ.get(ENV_PATH_KEY)
    print(f"reading ENV_PATH_KEY {env_path} from env")
    if env_path:
        # create if file not exist
        if not os.path.exists(env_path):
            with open(env_path, 'w', encoding="utf-8"):
                pass
        existing_data = {}
        # load old data
        with open(env_path, 'r', encoding="utf-8") as file:
            if os.path.getsize(env_path) > 0:
                file.seek(0)
                existing_data = json.load(file)

        # combine and write
        with open(env_path, 'w', encoding="utf-8") as file:
            combined_data = {**existing_data, **{env_schema.key: env_schema.value for env_schema in env_schemas}}
            file.seek(0)
            file.truncate()
            json.dump(combined_data, file, ensure_ascii=False)
    else:
        print("no ENV_PATH_KEY found")
