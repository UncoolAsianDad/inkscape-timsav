#!/usr/bin/env python
'''
Copyright (c) 2010 MakerBot Industries

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''
import sys,os
import inkex
from math import *
import getopt
from unicorn.context import GCodeContext
from unicorn.svg_parser import SvgParser

class MyEffect(inkex.Effect):
  def __init__(self):
    inkex.Effect.__init__(self)
    self.arg_parser.add_argument("--pen-up-cmd",
                      action="store", type=str,
                      dest="pen_up_cmd", default="M5",
                      help="Pen Up Command")
    self.arg_parser.add_argument("--pen-down-cmd",
                      action="store", type=str,
                      dest="pen_down_cmd", default="M3",
                      help="Pen Down Command")
    self.arg_parser.add_argument("--pen-down-angle",
                      action="store", type=float,
                      dest="pen_down_angle", default="90.0",
                      help="Pen Down Angle")
    self.arg_parser.add_argument("--pen-score-angle",
                      action="store", type=float,
                      dest="pen_score_angle", default="45.0",
                      help="Pen Score Angle")
    self.arg_parser.add_argument("--pen-draw-angle",
                      action="store", type=float,
                      dest="pen_mark_angle", default="10.0",
                      help="Pen Mark Angle")
    self.arg_parser.add_argument("--start-delay",
                      action="store", type=float,
                      dest="start_delay", default="1",
                      help="Delay after pen down command before movement in seconds")
    self.arg_parser.add_argument("--stop-delay",
                      action="store", type=float,
                      dest="stop_delay", default="1.0",
                      help="Delay after pen up command before movement in seconds")
    self.arg_parser.add_argument("--xy-feedrate",
                      action="store", type=float,
                      dest="xy_feedrate", default="3500.0",
                      help="XY axes feedrate in mm/min")
    self.arg_parser.add_argument("--xy-travelrate",
                      action="store", type=float,
                      dest="xy_travelrate", default="7000.0",
                      help="XY axes travelrate in mm/min")
    self.arg_parser.add_argument("--z-feedrate",
                      action="store", type=float,
                      dest="z_feedrate", default="150.0",
                      help="Z axis feedrate in mm/min")
    self.arg_parser.add_argument("--z-height",
                      action="store", type=float,
                      dest="z_height", default="0.0",
                      help="Z axis print height in mm")
    self.arg_parser.add_argument("--finished-height",
                      action="store", type=float,
                      dest="finished_height", default="0.0",
                      help="Z axis height after printing in mm")
    self.arg_parser.add_argument("--x-home",
                      action="store", type=float,
                      dest="x_home", default="0.0",
                      help="Starting X position")
    self.arg_parser.add_argument("--y-home",
                      action="store", type=float,
                      dest="y_home", default="0.0",
                      help="Starting Y position")
    self.arg_parser.add_argument("--num-copies",
                      action="store", type=int,
                      dest="num_copies", default="1")
    self.arg_parser.add_argument("--continuous",
                      action="store", type=str,
                      dest="continuous", default="false",
                      help="Plot continuously until stopped.")
    self.arg_parser.add_argument("--tab",
                      action="store", type=str,
                      dest="tab")

  def save_raw(self, ret):
    self.context.generate()

  def effect(self):
    self.context = GCodeContext(self.options.xy_feedrate,self.options.xy_travelrate,
                           self.options.start_delay, self.options.stop_delay,
                           self.options.pen_up_cmd,
                           self.options.pen_down_cmd,
                           self.options.pen_down_angle, self.options.pen_score_angle, self.options.pen_mark_angle,
                           self.options.continuous,
                           self.options.input_file)
    parser = SvgParser(self.document.getroot())
    parser.parse()
    for entity in parser.entities:
      entity.get_gcode(self.context)

if __name__ == '__main__':   #pragma: no cover
  e = MyEffect()
  e.run()
