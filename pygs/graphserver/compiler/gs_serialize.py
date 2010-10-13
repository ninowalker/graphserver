from optparse import OptionParser
from graphserver.graphdb import GraphDatabase
import os

def main():
    usage = """usage: python gs_serialize.py [options] <basename> <graphdb_filename> """
    parser = OptionParser(usage=usage)
    parser.add_option("-m", "--memmap",
                      action="store_true", dest="memmap", default=False,
                      help="Create a memmap serialized file.")
    
    (options, args) = parser.parse_args()
    
    if len(args) != 2:
        parser.print_help()
        exit(-1)
    
    basename, graphdb_filename = args
    
    db = GraphDatabase(graphdb_filename)
    g = db.incarnate()
    g.serialize(basename, options.memmap)
    print "done"

if __name__=='__main__':
    main()