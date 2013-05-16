#!/usr/bin/env python
import sys
import argparse
import bencode

parser = argparse.ArgumentParser()

parser.add_argument('-a', '--announce', nargs=1, help="Announce URL(s) to set in outfile. http://tracker1,http://tracker2,...")
parser.add_argument('-p', '--private', action='store_const', const=1, default=0, help="Set private flag. Changes info_hash.")
parser.add_argument('-c', '--created-by', nargs=1, help="Created by (string).")
parser.add_argument('-co', '--comment', nargs=1, help="Comment.")
parser.add_argument('-d', '--date', nargs=1, help="Creation date (unix timestamp).")

parser.add_argument('-s', '--strip', action='store_const', const=True, default=False, help="Strip output file.")
parser.add_argument('-r', '--really-strip', action='store_const', const=True, default=False, help="Also strip the info dict. Changes the info_hash - .torrent will be incompatible.")

parser.add_argument('src', nargs='?', type=argparse.FileType('rb'), default=sys.stdin)
parser.add_argument('dest', nargs='?', type=argparse.FileType('wb'), default=sys.stdout)

args = parser.parse_args()

if args.src == sys.stdin and sys.stdin.isatty():
	parser.print_help()
	exit()

if args.dest == sys.stdout and sys.stdout.isatty():
	sys.stderr.write("Not writing binary data to a terminal.\n")
	exit()

meta = bencode.bdecode( args.src.read() )
args.src.closed

if args.strip:
	meta = {'info': meta['info']}

if args.really_strip:
	meta = {'info': {
				'files': meta['info']['files'],
				'pieces': meta['info']['pieces'],
				'piece length': meta['info']['piece length']}
			}

if 'private' in meta['info'] and not args.private:
	meta['info']['private'] = 0
elif args.private:
	meta['info']['private'] = 1

if args.announce:
	announce_list = args.announce[0].split(',')
	# If multiple trackers, set the announce list dict	
	if ( len(announce_list) > 1 ):
		meta['announce-list'] = [announce_list]
		if 'announce' in meta:
			del meta['announce']
	else:
		meta['announce'] = announce_list[0]
		if 'announce-list' in meta:
			del meta['announce-list']

if args.created_by:
	meta['created by'] = args.created_by

if args.comment:
	meta['comment'] = args.comment

args.dest.write( bencode.bencode(meta) )
