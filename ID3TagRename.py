#!/usr/bin/python
#
# =============================================================================
#  Version: 1.2 (July 31, 2013)
#  Author: Jeff Puchalski (jpp13@cornell.edu)
#
# =============================================================================
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================

import sys, os, re, argparse, fnmatch
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3

# Glob pattern of files to include
includes = [ '*.mp3' ]
# Transform glob pattern to regular expression
includes = r'|'.join([fnmatch.translate(x) for x in includes])

def rename_file(dirpath, fname, album_naming, clear_comments):
    file = os.path.join(dirpath, fname)

    try:
        audio = EasyID3(file)
    except:
        sys.stderr.write("Error processing file %s" % fname)
        return
    
    if album_naming:
        tracknum = re.sub(r'([0-9]+)/.*', r'\1', audio["tracknumber"][0])
        newname = ''.join([ audio['artist'][0], ' -', format("%02d" % int(tracknum)), '- ' ])
    else:
        newname = ''.join([ audio['artist'][0], ' - ' ])
    newname = ''.join([ newname, audio['title'][0], '.mp3' ])
    # Drop punctuation from the new file name
    newname = newname.translate(dict((ord(c), None) for c in u'"*/:<>?\|'))
    
    new_file = os.path.join(dirpath, newname)
    
    try:
        os.rename(file, new_file)
    except:
        sys.stderr.write("Error processing file %s" % fname)
        return
    
    if clear_comments:
        audio = ID3(new_file)
        audio.delall('COMM')
        audio.save()
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.1')
    parser.add_argument('-a', '--album-naming', action='store_true',
                        help='Album naming scheme (artist-tracknum-title)')
    parser.add_argument('-c', '--clear-comments', action='store_true',
                        help='Clear MP3 comments field')
    parser.add_argument('-R', '--recursive', action='store_true', default=False,
                        help='Process subdirectories recursively')
    parser.add_argument('directory', nargs='?', default='.',
                        help='Directory in which to process files')
                        
    args = parser.parse_args()

    for (dirpath, dirnames, filenames) in os.walk(args.directory):
        filenames = [f for f in filenames if re.match(includes, f)]
        for fname in filenames:
            rename_file(dirpath, fname, args.album_naming, args.clear_comments)
        if not args.recursive: break

if __name__ == '__main__':main()