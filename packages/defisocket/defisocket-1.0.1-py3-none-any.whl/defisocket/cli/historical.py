import asyncio
import json
from dataclasses import asdict
import os
import logging
from defisocket.stream import HistoricalStream, Substream

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if logger.hasHandlers(): logger.handlers.clear()
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(handler)
logger.propagate = False

if __name__ == '__main__':
    load_dotenv()
    import argparse

    async def main():

        DEFISOCKET_URL= os.getenv('DEFISOCKET_URL')
        if not DEFISOCKET_URL:
            error = 'Please set DEFISOCKET_URL in .env file'
            logger.error(error)
            raise Exception(error)

        parser = argparse.ArgumentParser(description='Historical Stream Management')

        command = parser.add_subparsers(dest='command')

        create_parser = command.add_parser('create', help='Create a new historical stream')
        create_parser.add_argument('-name', type=str, required=True, help='Name of the historical stream to create')
        create_parser.add_argument('-networks', type=str, nargs='+', required=True, help='Networks for the historical stream (e.g., ETH BSC)')
        create_parser.add_argument('-starts', type=int, nargs='+', required=True, help='Start blocks for each network (e.g., 1000000 2000000)')
        create_parser.add_argument('-ends', type=int, nargs='+', required=True, help='End blocks for each network (e.g., 2000000 3000000)')
        create_parser.add_argument('-event-name', type=str, required=True, help='Event name for the historical stream (e.g., erc_20_all_events)')
        create_parser.add_argument('-client-name', type=str, required=True, help='Client name for the historical stream (e.g., erc20)')
        create_parser.add_argument('-wait', action="store_true", help='Wait for the stream to finish before returning')

        create_parser.add_argument('-extra-args', type=str, default='{}', help='Extra arguments for the substream in JSON format (e.g., \'{"tokens": ["USDT", "USDC"], "exclude_zero_transfers": true}\')')

        running_parser = command.add_parser('running', help='Get whether a historical stream is running or not')
        running_parser.add_argument('-name', type=str, required=True, help='Name of the historical stream to get running status for')

        progress_parser = command.add_parser('progress', help='Get progress of a historical stream')
        progress_parser.add_argument('-name', type=str, required=True, help='Name of the historical stream to get progress for')

        remove_parser = command.add_parser('remove', help='Remove a historical stream')
        remove_parser.add_argument('-name', type=str, required=True,help='Name of the historical stream to remove')

        stop_parser = command.add_parser('stop', help='Stop a historical stream')
        stop_parser.add_argument('-name', type=str, required=True, help='Name of the historical stream to stop')

        list_parser = command.add_parser('list', help='List downloaded files of a historical stream')
        list_parser.add_argument('-name', type=str, required=True, help='Name of the historical stream to list files for')

        download_parser = command.add_parser('download', help='Download a file from a historical stream')
        download_parser.add_argument('-name', type=str, required=True, help='Name of the historical stream to download from')
        download_parser.add_argument('-network', required=True, type=str, help='Network of the file to download')
        download_parser.add_argument('-file', required=True, type=str, help='Network of the file to download')

        args = parser.parse_args()
        logger.info(args)

        if args.command == 'create':
            networks = args.networks
            starts = args.starts
            ends = args.ends
            wait = args.wait
            print(wait)
            block_ranges = {networks[i]: (starts[i], ends[i]) for i in range(len(networks))}

            extra_args = json.loads(args.extra_args)


            substream = Substream(
                client_name=args.client_name,
                name=args.event_name,
                networks=networks,
                extra_args=extra_args
            )

            logger.info(f"Creating stream: {args.name} with networks {networks} and block ranges {block_ranges}")
            logger.info(asdict(substream))

            stream = HistoricalStream(name=args.name, server_address=DEFISOCKET_URL)
            if wait:
                res = await stream.start_and_wait(substream=substream, block_ranges=block_ranges, sleep_time=3)
            else:
                res = stream.start(substream=substream, block_ranges=block_ranges)
            logger.info(res)

        elif args.command == 'running':
            stream = HistoricalStream(name=args.name, server_address=DEFISOCKET_URL)
            res = stream.is_running()
            logger.info(res)

        elif args.command == 'progress':
            stream = HistoricalStream(name=args.name, server_address=DEFISOCKET_URL)
            res = stream.get_progress()
            logger.info(res)

        elif args.command == 'stop':
            stream = HistoricalStream(name=args.name, server_address=DEFISOCKET_URL)
            res = stream.stop()
            logger.info(res)

        elif args.command == 'remove':
            stream = HistoricalStream(name=args.name, server_address=DEFISOCKET_URL)
            res = stream.remove()
            logger.info(res)

        elif args.command == 'list':
            stream = HistoricalStream(name=args.name, server_address=DEFISOCKET_URL)
            res = stream.list_downloaded_files()
            logger.info(res)

        elif args.command == 'download':
            stream = HistoricalStream(name=args.name, server_address=DEFISOCKET_URL)
            stream.download_file(network=args.network, file_name=args.file)

    asyncio.run(main())
