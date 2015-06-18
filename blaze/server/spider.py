#!/usr/bin/env python

from __future__ import absolute_import

import os

from odo import resource
from odo.utils import ignoring

from .server import Server, DEFAULT_PORT


__all__ = 'spider',


def _spider(resource_path, ignore, followlinks, hidden):
    resources = {}
    for filename in (os.path.join(resource_path, x)
                     for x in os.listdir(resource_path)):
        basename = os.path.basename(filename)
        if (basename.startswith(os.curdir) and not hidden or
                os.path.islink(filename) and not followlinks):
            continue
        if os.path.isdir(filename):
            new_resources = _spider(filename, ignore=ignore,
                                    followlinks=followlinks, hidden=hidden)
            if new_resources:
                resources[basename] = new_resources
        else:
            with ignoring(*ignore):
                resources[basename] = resource(filename)
    return resources


def spider(resource_path, ignore=(ValueError, NotImplementedError),
           followlinks=True, hidden=False):
    return {
        os.path.basename(resource_path): _spider(resource_path, ignore=ignore,
                                                 followlinks=followlinks,
                                                 hidden=hidden)
    }


def from_yaml(filename, ignore=(ValueError, NotImplementedError),
              followlinks=True, hidden=False):
    import yaml
    with open(filename, 'rt') as f:
        spec = yaml.load(f.read())
    resources = {}
    for name, info in spec.items():
        if 'uri' not in info:
            raise ValueError('uri not found for data source %r' % name)
        uri = info['uri']
        if os.path.isdir(uri):
            resources = spider(os.path.expanduser(uri),
                               ignore=ignore,
                               followlinks=followlinks,
                               hidden=hidden)
        else:
            resources[name] = resource(uri, dshape=info.get('dshape'))
    return resources


def _parse_args():
    import argparse
    p = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('path', type=str,
                   help=('A directory to recurse into or a YAML file '
                         'specifying the resources to conjure up'))
    p.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                   help='Port number')
    p.add_argument('-l', '--follow-links', action='store_true',
                   help='Follow links when listing files')
    p.add_argument('-e', '--ignored-exception', nargs='*',
                   default=['Exception'],
                   help='Exceptions to ignore when calling resource on a file')
    p.add_argument('-H', '--hidden', action='store_true',
                   help='Call resource on hidden files')
    return p.parse_args()


def _main():
    args = _parse_args()
    path = os.path.expanduser(args.path)
    ignore = tuple(getattr(__builtins__, e) for e in args.ignored_exceptions)
    hidden = args.hidden
    followlinks = args.follow_links
    func = spider if os.path.isdir(path) else from_yaml(path)
    resources = func(path, ignore=ignore, followlinks=followlinks,
                     hidden=hidden)
    Server(resources).run(port=args.port)


if __name__ == '__main__':
    _main()
