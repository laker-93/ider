import asyncio
import logging
from argparse import ArgumentParser
from typing import Dict

import uvicorn

from ider.utils.init_logger import initialise_logger
from ider.utils.registration import get_config, create_app

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-e", "--env", default="dev", help="The environment to run the app with")
    args = arg_parser.parse_args()

    app_config = get_config(args.env)

    initialise_logger(
        app_config["application_settings"]["app_name"],
        level=app_config["application_settings"]["logging_level"],
        disable_file_handler=True
    )

    app = create_app(app_config)
    uvicorn.run(app,  host=app_config["application_settings"]["app_host"], port=app_config["application_settings"]["app_port"])