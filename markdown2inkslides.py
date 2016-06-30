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

from my_eqtexsvg import *
from my_inksyntax import *
from mistune_math import MarkdownWithMath

def debug_print(msg):
  """stdout of this script is interpreted as svg, so we need to log debug messages elsewhere."""
  with open('/tmp/test.txt', 'w') as tmpfile:
       tmpfile.write(msg)

def handle_header(self, line):
    titletext = line
    already_existing_layer = self.svg.find('.//{http://www.w3.org/2000/svg}g[@id="md2i_layer%i"]' % (self.layercounter))
    if already_existing_layer is None:
      self.layers.append(inkex.etree.SubElement(self.svg, 'g'))
      self.layer = self.layers[-1]
      self.layer.set(inkex.addNS('label', 'inkscape'), 'layer%s' % (self.layercounter))
      self.layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
      self.layer.set('id', 'md2i_layer%i' % (self.layercounter) )
      # write slide number
      text = inkex.etree.Element(inkex.addNS('text','svg'))
      text.set('id', 'md2i_layer%i_slidenumber' % (self.layercounter) )
      text.text = str(self.layercounter)
      style = {'font-size': '20px',  'font-family': 'Source Serif Pro'}
      text.set('style', formatStyle(style))
      # lower right corner
      text.set('x', str(11.5 * self.width / 12.))
      text.set('y', str(11.5 * self.height / 12.))
      self.layer.append(text)
      # write title
      title = inkex.etree.Element(inkex.addNS('text','svg'))
      title.set('id', 'layer%i_title' % (self.layercounter) )
      title.text = titletext
      # lower right corner
      title.set('x', str(1 * self.width / 12.))
      title.set('y', str(1 * self.height / 12.))
      style = {'font-size': '36px',  'font-family': 'Source Serif Pro'}
      title.set('style', formatStyle(style))
      self.layer.append(title)
    else:
      # update title
      self.layers.append(already_existing_layer)
      self.layer = self.layers[-1]
      title = already_existing_layer.find('.//{http://www.w3.org/2000/svg}text[@id="md2i_layer%i_title"]' % (self.layercounter))
      if title is not None:
        title.text = titletext
    self.layercounter += 1
    self.textcounter = 0
    self.imagecounter = 0

def handle_text(self, line):
    already_existing_text = self.svg.find('.//{http://www.w3.org/2000/svg}text[@id="md2i_layer%i_text%i"]' % (self.layercounter, self.textcounter))
    if already_existing_text is None:
      text = inkex.etree.Element(inkex.addNS('text','svg'))
      text.text = line
      text.set(inkex.addNS('myId','md2i'), "md2i_layer%i_text%i" % (self.layercounter, self.textcounter))
      text.set('x', str(self.width / 10.))
      text.set('y', str(self.textcounter * self.height / 15. + self.height/3.5))
      text.set('id', "md2i_layer%i_text%i" % (self.layercounter, self.textcounter))
      #style = {'text-align' : 'center', 'text-anchor': 'middle'}
      style = {'font-size': '28px',  'font-family': 'Source Serif Pro'}
      text.set('style', formatStyle(style))
      self.layer.append(text)
    else:
      already_existing_text.text = line
    self.textcounter += 1

def handle_image(self, src):
    already_existing_image = self.svg.find('.//{http://www.w3.org/2000/svg}image[@id="md2i_layer%i_image%i"]' % (self.layercounter, self.imagecounter))
    if already_existing_image is None:
      image = inkex.etree.Element(inkex.addNS('image','svg'))
      image.set(inkex.addNS('href','xlink'), src)
      image.set(inkex.addNS('absref','sodipodi'), os.environ['PWD'] + '/' + src) 
      image.set('x', str(self.width / 10.))
      image.set('y', str(self.height / 3.5))
      image.set('id', 'md2i_layer%i_image%i' % (self.layercounter, self.imagecounter))
      style = {'image-align' : 'center', 'image-anchor': 'middle'}
      image.set('style', formatStyle(style))
      self.layer.append(image)
    else:
      already_existing_image.set(inkex.addNS('href','xlink'), src)
      already_existing_image.set(inkex.addNS('absref','sodipodi'), os.environ['PWD'] + '/' + src) 
    self.imagecounter +=1

def handle_math(self, text, packages=""):
    latex_effect(self, text, packages) 
    return "m"

def handle_code(self, text, packages=""):
    inserter(self, 'Python', text)
    return "c"

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
        handle_text(self, link)
        return "a"
    def block_code(self, code, lang):
        handle_code(self, code)
        return "c"
    def codespan(self, text):
        handle_code(self, text)
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
    def block_math(self, text):
        handle_math(self, text, "")
        return 'm' % text
    def latex_environment(self, name, text):
        handle_text(self, text)
        return 'm'
    def inline_math(self, text):
        handle_math(self,  text, "")
        return 'm'


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
          type = 'string', dest = 'what', default = 'test.md',
          help = 'Which markdown file do you want to turn to slides?')

    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method.
        """
        # Get script's "--what" option value.
        what = self.options.what # filename of markdown file

        renderer = InkslideRenderer(self)
        markdown = MarkdownWithMath(renderer=renderer)
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
