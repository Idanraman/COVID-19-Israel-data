import json
from datetime import datetime, timezone
import os
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import time
import logging
import sys

sys.path.append("../")
sys.path.insert(1,"./personal_data/")

from cities_parser import cities_filename_verifier

OUTPUT_DIR_CITIES = os.path.join('..','telegram_files','raw_cities_files')

script_dir = os.path.dirname(__file__)
abs_file_path = os.path.join(script_dir, 'personal_data','personal_data.txt')

with open(abs_file_path, mode="r") as file:
    personal_data = file.readlines()
    api_id = int(personal_data[0].replace("\n", ""))
    api_hash = personal_data[1].replace("\n", "")
    phone_number = personal_data[2]
    client = TelegramClient(session="mysession", api_id=api_id, api_hash=api_hash)


async def main(channel_name):
    await client.start(phone=lambda: [phone_number])
    logging.info("Client Created")

    channel_url = f"https://t.me/{channel_name}"
    logging.info(f"Channel URL: {channel_url}")
    channel = await client.get_entity(channel_url)

    offset_id = 0
    all_messages = []
    total_count_limit = 10000
    downloaded_messages = {}
    in_time_range = True

    while in_time_range:
        history = await client(
            GetHistoryRequest(
                peer=channel,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=100,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
        if not history.messages:
            break

        for message in history.messages:
            if (
                message.file is not None
                and message.file.name
                and message.file.size <= 10000000
            ):
                new_file_name = message.date.strftime("%Y-%m-%d") + "_" + message.file.name
                if new_file_name not in os.listdir(os.path.join(script_dir,OUTPUT_DIR_CITIES)) \
                        and cities_filename_verifier(new_file_name):
                    filename = await client.download_media(
                        message=message,
                        file=os.path.join(script_dir,OUTPUT_DIR_CITIES,new_file_name),
                    )
                    logging.info(f"Downloading {filename}")
                else:
                    filename = message.file.name

                downloaded_messages[message.file.name] = message.date.strftime(
                    "%Y-%m-%d"
                )
            else:
                filename = None

            message_dict = message.to_dict()
            if filename is not None:
                message_dict["attached_file"] = filename

            all_messages.append(message_dict)
            if all_messages[-1]["date"] < datetime(
                2019, 12, 1, 0, 0, 0, tzinfo=timezone.utc
            ):
                in_time_range = False
                logging.info("Reached 01-12-2019, Stops loading old messages.")
                break

        offset_id = all_messages[-1]["id"]
        logging.info(f'Date: {all_messages[-1]["date"]}')
        logging.info(f"Total messages: {len(all_messages)}/{total_count_limit}")

        if len(all_messages) >= total_count_limit:
            break

    # class to parse datetime to json
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()

            if isinstance(o, bytes):
                return list(o)

            return json.JSONEncoder.default(self, o)


def main_runner():
    channels = ["MOHreport"]
    start_time = time.perf_counter()
    for channel_name in channels:
        with client:
            client.loop.run_until_complete(main(channel_name))
    end_time = time.perf_counter()
    logging.info(f"Telegram Bot finished in {round(end_time - start_time)} seconds")


if __name__ == '__main__':
    main_runner()