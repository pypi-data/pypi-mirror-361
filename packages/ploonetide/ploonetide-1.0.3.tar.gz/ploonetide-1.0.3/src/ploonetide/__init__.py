#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################################
#                                                                        #
# .#####..##......####...####..##..##.######.######.######.#####..######.#
# .##..##.##.....##..##.##..##.###.##.##.......##.....##...##..##.##.....#
# .#####..##.....##..##.##..##.##.###.####.....##.....##...##..##.####...#
# .##.....##.....##..##.##..##.##..##.##.......##.....##...##..##.##.....#
# .##.....######..####...####..##..##.######...##...######.#####..######.#
# .......................................................................#
#                                                                        #
# Ploonetide                                                             #
# Simmer of  moons on eccentric orbits via viscoelastic tidal heating    #
#                                                                        #
##########################################################################
# Jaime A. Alvarado-Montes (C) 2022                                      #
##########################################################################

from __future__ import absolute_import

import platform
import logging
import os
PACKAGEDIR = os.path.abspath(os.path.dirname(__file__))
MPLSTYLE = '{}/data/ploonetide.mplstyle'.format(PACKAGEDIR)

# By default Matplotlib is configured to work with a graphical user interface
# which may require an X11 connection (i.e. a display).  When no display is
# available, errors may occur.  In this case, we default to the robust Agg backend.
if platform.system() == "Linux" and os.environ.get('DISPLAY', '') == '':
    import matplotlib
    matplotlib.use('Agg')

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

from .ploonetide import *
from .version import __version__
