#!/usr/bin/python
#
# =============================================================================
#  Version: 1.0 (January 24, 2013)
#  Author: Jeff Puchalski (jpp13@cornell.edu)
#
# =============================================================================
# Copyright (c) 2013 Jeff Puchalski

# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
# =============================================================================

"""ID3TagRename:
Rename MP3 files based on ID3 tag attributes.

Usage: ID3TagRename.py [options]

Options:
  -a, --album-naming   : album naming scheme (track-title)
  -c, --clear-comments : clear comments field
  -d, --directory=dir  : process files in dir
  -h, --help           : display this help and exit
  -v, --verbose        : verbose output
  
Dependencies:
  mutagen (>=1.20) Python multimedia tagging library
    http://code.google.com/p/mutagen/
"""

import sys, os, os.path, getopt
from fnmatch import fnmatch
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3

version = '1.0'

def rename_file(dir, file):
    try:
        audio = EasyID3(file)
    except:
        if verbose: print >> sys.stderr, 'Skipping %s' % file
        return
        
    if verbose: print "Processing %s" % file
    
    if album_naming:
        name = ''.join([ format("%02d" % int(audio["tracknumber"][0])), '-' ])
    else:
        name = ''.join([ audio['artist'][0], ' - ' ])
    name = ''.join([ name, audio['title'][0], '.mp3' ])
    # Drop invalid punctuation from the new file name that may have been in the tag
    name = name.translate(dict((ord(c), None) for c in u'"*/:<>?\|'))
    
    new_file = os.path.join(dir, name)
    if verbose: print "Renaming to %s" % new_file
    os.rename(file, new_file)
    
    if clear_comments:
        audio = ID3(new_file)
        audio.delall('COMM')
        audio.save()

def get_files(dir):
    if not os.path.isdir(dir):
        print >> sys.stderr, "Error: %s is not a valid directory" % dir
        sys.exit(1)
    if os.path.islink(dir):
        print >> sys.stderr, "Error: symbolic links not supported"
        sys.exit(1)
        
    return [os.path.join(dir, f) for f in sorted(os.listdir(dir)) if fnmatch(f, '*.mp3')]
    
def show_help():
    print >> sys.stdout, __doc__,

def show_usage(script_name):
    print >> sys.stderr, 'Usage: %s [options]' % script_name

def main():
    script_name = os.path.basename(sys.argv[0])

    try:
        long_opts = ['album-naming', 'clear-comments', 'directory=', 'help', 'verbose', 'version']
        opts, args = getopt.getopt(sys.argv[1:], "achd:vV", long_opts)
    except getopt.GetoptError:
        show_usage(script_name)
        sys.exit(1)
    
    global verbose, album_naming, clear_comments
    verbose = False
    album_naming = False
    clear_comments = False
    directory = '.'
    
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            show_help()
            sys.exit()
        elif opt in ('-a', '--album-naming'):
            album_naming = True
        elif opt in ('-c', '--clear-comments'):
            clear_comments = True
        elif opt in ('-d', '--directory'):
            directory = arg
        elif opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ('-V', '--version'):
            print script_name, ' version: ', version
            sys.exit(0)
            
    if len(args) > 0:
        show_usage(script_name)
        sys.exit(4)
        
    for file in get_files(directory):
        rename_file(directory, file)

if __name__ == '__main__':main()