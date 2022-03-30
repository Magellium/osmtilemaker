#!/usr/bin/env python

# adapted from https://github.com/openstreetmap/mapnik-stylesheets/blob/master/generate_tiles.py

import argparse
import logging
import os
import sys
import threading
from queue import Queue
from math import pi,sin,log,exp,atan
try:
    import mapnik2 as mapnik
except:
    import mapnik

# declare logger
logger = logging.getLogger("genTile")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(name)s LOG> %(asctime)s: line %(lineno)d: %(levelname)s: %(message)s',
    "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

def closeLoggingStreamHandlers():
    logger.debug('Close logging streamHandlers')
    for handler in logger.handlers:
        handler.close()
        logger.removeFilter(handler)

# some variables
DEG_TO_RAD = pi/180
RAD_TO_DEG = 180/pi

def minmax (a,b,c):
    a = max(a,b)
    a = min(a,c)
    return a

class GoogleProjection:
    def __init__(self,levels=18):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0,levels):
            e = c/2
            self.Bc.append(c/360.0)
            self.Cc.append(c/(2 * pi))
            self.zc.append((e,e))
            self.Ac.append(c)
            c *= 2

    def fromLLtoPixel(self,ll,zoom):
        d = self.zc[zoom]
        e = round(d[0] + ll[0] * self.Bc[zoom])
        f = minmax(sin(DEG_TO_RAD * ll[1]),-0.9999,0.9999)
        g = round(d[1] + 0.5*log((1+f)/(1-f))*-self.Cc[zoom])
        return (e,g)

    def fromPixelToLL(self,px,zoom):
        e = self.zc[zoom]
        f = (px[0] - e[0])/self.Bc[zoom]
        g = (px[1] - e[1])/-self.Cc[zoom]
        h = RAD_TO_DEG * ( 2 * atan(exp(g)) - 0.5 * pi)
        return (f,h)



class RenderThread:
    def __init__(self, tile_dir, mapfile, q, maxZoom):
        self.tile_dir = tile_dir
        self.q = q
        self.m = mapnik.Map(256, 256)
        # Load style XML
        mapnik.load_map(self.m, mapfile, False)
        # Obtain <Map> projection
        self.prj = mapnik.Projection(self.m.srs)
        # Projects between tile pixel co-ordinates and LatLong (EPSG:4326)
        self.tileproj = GoogleProjection(maxZoom+1)


    def render_tile(self, tile_uri, x, y, z):

        # Calculate pixel positions of bottom-left & top-right
        p0 = (x * 256, (y + 1) * 256)
        p1 = ((x + 1) * 256, y * 256)

        # Convert to LatLong (EPSG:4326)
        l0 = self.tileproj.fromPixelToLL(p0, z)
        l1 = self.tileproj.fromPixelToLL(p1, z)

        # Convert to map projection (e.g. mercator co-ords EPSG:900913)
        c0 = self.prj.forward(mapnik.Coord(l0[0],l0[1]))
        c1 = self.prj.forward(mapnik.Coord(l1[0],l1[1]))

        # Bounding box for the tile
        if hasattr(mapnik,'mapnik_version') and mapnik.mapnik_version() >= 800:
            bbox = mapnik.Box2d(c0.x,c0.y, c1.x,c1.y)
        else:
            bbox = mapnik.Envelope(c0.x,c0.y, c1.x,c1.y)
        render_size = 256
        self.m.resize(render_size, render_size)
        self.m.zoom_to_box(bbox)
        if(self.m.buffer_size < 128):
            self.m.buffer_size = 128

        # Render image with default Agg renderer
        im = mapnik.Image(render_size, render_size)
        mapnik.render(self.m, im)
        im.save(tile_uri, 'png256')


    def loop(self):
        try:
            while True:
                #Fetch a tile from the queue and render it
                r = self.q.get()
                if (r == None):
                    self.q.task_done()
                    break
                else:
                    (name, tile_uri, x, y, z) = r

                exists= ""
                if os.path.isfile(tile_uri):
                    exists= ", exists"
                else:
                    try:
                        self.render_tile(tile_uri, x, y, z)
                    except:
                        logging.exception("message")
                        logger.error('Exception generating tile: '+ str(tile_uri)+', '+ str(z)+', '+ str(x)+', '+ str(y))
                        self.q.task_done()
                        break
                empty= ''
                try:
                    bytes=os.stat(tile_uri)[6]
                    if bytes == 103:
                        empty = ", empty"
                except:
                    pass
                logger.info('Rendered: '+name+': '+ str(z)+', '+ str(x)+', '+ str(y)+', queued: '+str(self.q.qsize())+exists+empty)
                self.q.task_done()
        except:
            logging("message")
            logger.critical('Uncaught exception in thread')
            os._exit(1)



def render_tiles(bbox, bbox_name, mapfile, tile_dir, minZoom, maxZoom, num_threads, tms_scheme=False):
    logger.info("render_tiles")

    # Launch rendering threads
    queue = Queue(32)
    renderers = {}
    for i in range(num_threads):
        renderer = RenderThread(tile_dir, mapfile, queue, maxZoom)
        render_thread = threading.Thread(target=renderer.loop)
        render_thread.start()
        logger.debug('Started render thread %s', render_thread.getName())
        renderers[i] = render_thread

    if not os.path.isdir(tile_dir):
        os.mkdir(tile_dir)

    gprj = GoogleProjection(maxZoom+1)

    ll0 = (bbox[0],bbox[3])
    ll1 = (bbox[2],bbox[1])

    logger.info('Creating renderer-tasks')
    for z in range(minZoom,maxZoom + 1):
        px0 = gprj.fromLLtoPixel(ll0,z)
        px1 = gprj.fromLLtoPixel(ll1,z)

        # check if we have directories in place
        zoom = "%s" % z
        if not os.path.isdir(tile_dir + zoom):
            os.mkdir(tile_dir + zoom)
        for x in range(int(px0[0]/256.0),int(px1[0]/256.0)+1):
            # Validate x co-ordinate
            if (x < 0) or (x >= 2**z):
                continue
            # check if we have directories in place
            str_x = "%s" % x
            if not os.path.isdir(tile_dir + zoom + '/' + str_x):
                os.mkdir(tile_dir + zoom + '/' + str_x)
            for y in range(int(px0[1]/256.0),int(px1[1]/256.0)+1):
                # Validate x co-ordinate
                if (y < 0) or (y >= 2**z):
                    continue
                # flip y to match OSGEO TMS spec
                if tms_scheme:
                    str_y = "%s" % ((2**z-1) - y)
                else:
                    str_y = "%s" % y
                tile_uri = tile_dir + zoom + '/' + str_x + '/' + str_y + '.png'
                # Submit tile to be rendered into the queue
                t = (bbox_name, tile_uri, x, y, z)
                try:
                    queue.put(t)
                except KeyboardInterrupt:
                    logging.info('Draining '+str(queue.qsize())+' items from the queue to stop quickly')
                    # clear the queue to stop quickly
                    with queue.mutex:
                        queue.clear()

                    raise SystemExit("Ctrl-c detected, exiting...")

    logging.info('Submitted all render-tasks, now waiting for remaining '+str(queue.qsize())+' to finish')

    # wait for pending rendering jobs to complete
    queue.join()

class TilesDirMustEndsWithSlash(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not values.endswith('/'):
            logger.debug('Tiles dir misses an end slash: %r' % (values))
            values = values + '/'
            setattr(namespace, self.dest, values)
            logger.debug('Let\'s add it: %r' % (values))
        else:
            logger.debug('%r end with slash: OK' % (values))

def main():
    parser = argparse.ArgumentParser(description='Render tiles.')
    parser.add_argument('--bbox',
                        nargs=4,
                        metavar=('minLong','minLat','maxLong','maxLat'),
                        type=float,
                        required=True,
                        dest='bbox',
                        help='Set the bbox on which tiles must be rendered.\
                             Example for Hamburg: \'(8.4213643278, 53.3949251389, 10.3242585128, 53.9644376366)\'')
    parser.add_argument('--bbox_name',
                        metavar='BBOX_NAME',
                        type=str,
                        required=True,
                        dest='bbox_name',
                        help='Just an alias for your bbox (for logging purposes)')
    parser.add_argument('--mapfile',
                        metavar='MAPFILE',
                        type=str,
                        required=True,
                        dest='mapfile',
                        help='XML file used by Mapnik load_map() function')
    parser.add_argument('--tile_dir',
                        metavar='TILEDIR',
                        type=str,
                        required=True,
                        dest='tile_dir',
                        action=TilesDirMustEndsWithSlash,
                        help='Output directory for generated tiles')
    parser.add_argument('--minZoom',
                        metavar='MINZOOM',
                        type=int,
                        required=True,
                        dest='minZoom',
                        help='Tiles must be rendered above this zoom (from zoom 1)')
    parser.add_argument('--maxZoom',
                        metavar='MAXZOOM',
                        type=int,
                        required=True,
                        dest='maxZoom',
                        help='Tiles must be rendered below this zoom (up to zoom 18)')
    parser.add_argument('--num_threads',
                        metavar='NUM_THREADS',
                        type=int,
                        required=True,
                        dest='num_threads',
                        help='Rendering threads to spawn, should be roughly equal to number of CPU cores available')
    args = parser.parse_args()
    logger.info('Given arguments: ')
    logger.info(args)
    logger.info(args.bbox)

    render_tiles(args.bbox, args.bbox_name, args.mapfile, args.tile_dir, args.minZoom, args.maxZoom, args.num_threads)

    logger.info('Tiles rendering completed')
    closeLoggingStreamHandlers()
    os._exit(0)

if __name__ == "__main__":
    main()
    closeLoggingStreamHandlers()
