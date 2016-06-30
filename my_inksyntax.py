#! /usr/bin/env python
# -*- coding: utf-8; -*-

'''
A source code syntax highlighter plugin for Inkscape.

:author: Xīcò <xico@atelo.org>
'''

__version__ = '0.1.2'

import os
import platform
import sys
from subprocess import PIPE, Popen
import traceback


import inkex
from simplestyle import *
from StringIO import StringIO


INKSYNTAX_NS = u"http://www.lyua.org/inkscape/extensions/inksyntax/"
SVG_NS = u"http://www.w3.org/2000/svg"
XLINK_NS = u"http://www.w3.org/1999/xlink"
XML_NS = u"http://www.w3.org/XML/1998/namespace"

ID_PREFIX = "inksyntax-"

NSS = {
      u'textext': INKSYNTAX_NS,
          u'svg': SVG_NS,
              u'xlink': XLINK_NS,
}


def hl_lang (s):
  '''Return the main highlight language name.'''
  if s.find ('(') < 0:
    return s
  return s[:s.find('(')].rstrip()


# Search for available highlighter backend and languages

USE_PYGMENTS = False
try:
    from pygments import highlight

    import pygments.lexers
    from pygments.formatters import SvgFormatter
    pygments_langs = {}
    for cls in pygments.lexers.LEXERS:
        if cls.endswith('Lexer'):
            pygments_langs[cls[:-5]] = getattr(pygments.lexers, cls)
    USE_PYGMENTS = True
except ImportError:
    pass

USE_HIGHLIGHT = False
try:
    p = Popen(['highlight', '--list-langs'], stdin=PIPE, stdout=PIPE)
    out = p.communicate()[0]
    # Get all available languages
    highlight_langs = {}
    for line in out.splitlines():
        if line.isspace() \
           or line.startswith('Installed language') \
           or line.startswith('Use name') \
           or not ':' in line:
            continue
        k, v = [x.strip() for x in line.split(':')]
        if k and not k.isspace():
            highlight_langs[k] = v
    USE_HIGHLIGHT = True
except OSError:
    pass

if not USE_PYGMENTS and not USE_HIGHLIGHT:
    raise RuntimeError("No source highlighter found!")



def inksyntax_effect(self,text, src_lang="python"):

    # Get previous highlighted text
    old_node, text = self.get_old()

    # Query missing information
    asker = AskText(text)
    asker.ask(lambda s, t, l: self.inserter(s, t, l))

def get_old(self):
    # Search amongst all selected <g> nodes
    for node in [self.selected[i] for i in self.options.ids
                 if self.selected[i].tag == '{%s}g' % SVG_NS]:
        # Return first <g> with a inksyntax:text attribute
        if '{%s}text' % INKSYNTAX_NS in node.attrib:
            return (node,
                    node.attrib.get('{%s}text' %
                                    INKSYNTAX_NS).decode('string-escape'))
    return None, ''

def apply_style_highlight(self, group):
    group.set('style', formatStyle({'font-size': '10',
                                    'font-family': 'Monospace'}))
    style = {
        'com':   {'fill': '#838183', 'font-style': 'italic'},
        'dir':   {'fill': '#008200'},
        'dstr':  {'fill': '#818100'},
        'esc':   {'fill': '#ff00ff'},
        'kwa':   {'fill': '#000000', 'font-weight': 'bold'},
        'kwb':   {'fill': '#830000'},
        'kwc':   {'fill': '#000000', 'font-weight': 'bold'},
        'kwd':   {'fill': '#010181'},
        'line':  {'fill': '#555555'},
        'num':   {'fill': '#2228ff'},
        'slc':   {'fill': '#838183', 'font-style': 'italic'},
        'str':   {'fill': '#ff0000'},
        'sym':   {'fill': '#000000'},
    }
    for txt in [x for x in group if x.tag == '{%s}text' % SVG_NS]:
        # Modify the line spacing
        line_spacing_factor = 0.65
        txt.set('y', str(line_spacing_factor * float(txt.get('y'))))
        # Preserve white spaces
        txt.attrib['{%s}space' % XML_NS] = 'preserve'
        # Set the highlight color
        for tspan in [x for x in txt if x.tag == '{%s}tspan' % SVG_NS]:
            cls = tspan.get('class')
            if cls in style:
                tspan.set('style', formatStyle(style[cls]))

def apply_style_pygments(self, group):
    pass

def inserter(self, syntax, text):#line_number=False):

    #stx_backend, stx = syntax
    stx_backend = 'ighlight'
    stx = syntax

    # Get SVG highlighted output as character string
    if stx_backend == 'highlight':
  # For highlight 2.x
        #cmd = ["highlight", "--syntax", stx, "--svg"]
  # For highlight 3.x
        cmd = ["highlight", "--syntax",
               hl_lang (stx), # Fix for hl 3.9
               "-O", "svg"]
        #if line_number:
        #    cmd.append("--line-number")
        p = Popen(cmd,
                  stdin=PIPE, stdout=PIPE)
        out = p.communicate(text)[0]
    else:
        out = highlight(text, pygments.lexers.PythonLexer(), SvgFormatter())

    # Parse the SVG tree and get the group element
    try:
        tree = inkex.etree.parse(StringIO(out))
    except inkex.etree.XMLSyntaxError:
        # Hack for highlight 2.12
        out2 = out.replace('</span>', '</tspan>')
        tree = inkex.etree.parse(StringIO(out2))
    group = tree.getroot().find('{%s}g' % SVG_NS)

    # Remove the background rectangle
    if group[0].tag == '{%s}rect' % SVG_NS:
        del group[0]

    # Apply a CSS style
    if stx_backend == 'highlight':
        apply_style_highlight(self, group)
    else:
        apply_style_pygments(self, group)

    # Set the attributes for modification
    group.attrib['{%s}text' % INKSYNTAX_NS] = text.encode('string-escape')

    # Add the SVG group to the document
    self.layer.append(group)

# Try to apply properties
#if 'font' in props:
#  fd = pango.FontDescription(props['font'])
#  group.set('style', formatStyle({'font-size': '%fpt' % (fd.get_size()/pango.SCALE),
#                                  'font-family': fd.get_family()}))


