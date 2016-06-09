#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
import os
sys.path.append('/usr/share/inkscape/extensions')


# We will use the inkex module with the predefined Effect base class.
import inkex

# The simplestyle module provides functions for style parsing.
from simplestyle import *

import mistune

def debug_print(msg):
  """stdout of this script is interpreted as svg, so we need to log debug messages elsewhere."""
  with open('/tmp/test.txt', 'w') as tmpfile:
       tmpfile.write(msg)

def handle_header(self, line):
    titletext = line
    already_existing_layer = self.svg.find('.//{http://www.w3.org/2000/svg}g[@id="layer%i"]' % (self.layercounter))
    if already_existing_layer is None:
      self.layers.append(inkex.etree.SubElement(self.svg, 'g'))
      self.layer = self.layers[-1]
      self.layer.set(inkex.addNS('label', 'inkscape'), 'layer%s' % (self.layercounter))
      self.layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
      self.layer.set('id', 'layer%i' % (self.layercounter) )
      # write slide number
      text = inkex.etree.Element(inkex.addNS('text','svg'))
      text.set('id', 'layer%i_slidenumber' % (self.layercounter) )
      text.text = str(self.layercounter)
      # lower right corner
      text.set('x', str(11 * self.width / 12.))
      text.set('y', str(11 * self.height / 12.))
      self.layer.append(text)
      # write title
      title = inkex.etree.Element(inkex.addNS('text','svg'))
      title.set('id', 'layer%i_title' % (self.layercounter) )
      title.text = titletext
      # lower right corner
      title.set('x', str(1 * self.width / 12.))
      title.set('y', str(1 * self.height / 12.))
      style = {'font-size': '36px',  'font-family': 'TeX Gyre Pagella'}
      title.set('style', formatStyle(style))
      self.layer.append(title)
    else:
      # update title
      self.layers.append(already_existing_layer)
      self.layer = self.layers[-1]
      title = already_existing_layer.find('.//{http://www.w3.org/2000/svg}text[@id="layer%i_title"]' % (self.layercounter))
      if title is not None:
        title.text = titletext
    self.layercounter += 1
    self.textcounter = 0

def handle_text(renderer, line):
    text = inkex.etree.Element(inkex.addNS('text','svg'))
    text.text = line
    text.set('x', str(renderer.width / 10.))
    text.set('y', str(renderer.textcounter * renderer.height / 15. + renderer.height/3.5))
    #style = {'text-align' : 'center', 'text-anchor': 'middle'}
    style = {'font-size': '28px',  'font-family': 'TeX Gyre Pagella'}
    text.set('style', formatStyle(style))
    renderer.layer.append(text)
    renderer.textcounter += 1

def handle_image(self, src):
    image = inkex.etree.Element(inkex.addNS('image','svg'))
    image.set(inkex.addNS('href','xlink'), src)
    image.set(inkex.addNS('absref','sodipodi'), os.environ['PWD'] + '/' + src) 
    image.set('x', str(self.width / 10.))
    image.set('y', str(self.height / 3.5))
    style = {'image-align' : 'center', 'image-anchor': 'middle'}
    image.set('style', formatStyle(style))
    self.layer.append(image)

class InkslideRenderer(mistune.Renderer):
    """ modifies svg, dummy string output not needed"""
    def __init__(self, inkex_effect):
        self.svg = inkex_effect.document.getroot()
        self.width  = inkex_effect.unittouu(self.svg.get('width'))
        self.height = inkex_effect.unittouu(self.svg.attrib['height'])
        self.layers = []
        self.layer = inkex.etree.SubElement(self.svg, 'g')
        self.layercounter = 0
        self.textcounter = 0
        mistune.Renderer.__init__(self)
    def header(self, text, level, raw=None):
        handle_header(self, text)
        return "h"
    def paragraph(self, text):
        handle_text(self, text)
        return "p"
    def image(self, src, title, alt_text):
        handle_image(self, src)
        return "i"
    def autolink(self, link, is_email=False):
        handle_text(self, text)
        return "a"
    def codespan(self, text):
        handle_text(self, text)
        return "a"
    def double_emphasis(self, text):
        handle_text(self, text)
        return "a"
    def link(self, link, title, content):
        handle_text(self, link)
        return "a"
    def inline_html(self, text):
        handle_text(self, text)
        return "a"
    def list_item(self, text):
        handle_text(self, text)
        return "li"

class Markdown2InkslidesEffect(inkex.Effect):
    def __init__(self):
        """
        Constructor.
        Defines the "--what" option of a script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)

        # Define string option "--what" with "-w" shortcut and default value "World".
        self.OptionParser.add_option('-w', '--what', action = 'store',
          type = 'string', dest = 'what', default = 'World',
          help = 'What would you like to greet?')

    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method.
        """
        # Get script's "--what" option value.
        what = self.options.what # filename of markdown file

        renderer = InkslideRenderer(self)
        markdown = mistune.Markdown(renderer=renderer)
        with open(what, 'r') as f:
            test = markdown(f.read())
            # does roughly the same as 
            #    for line in f:
            #        if line[0] == '#':
            #          handle_header(line)
            #        elif line[0] == '!':
            #          handle_image(line)
            #        else:
            #          handle_text(line)

# Create effect instance and apply it.
effect = Markdown2InkslidesEffect()
effect.affect()
