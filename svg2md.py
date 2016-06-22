
#TODO: bring up to date and continue

from lxml import etree

infilename = 'test.svg'
with open(infilename) as f:
    file_content = f.read()

outfilename = "test2.md"
outfile_content = []

tree = etree.fromstring(file_content)
print tree
for e in tree[3:]:
  c = e.getchildren()
  if c:
    t = c[0]
    if t.text:
        outfile_content.append("# " + t.text)
    for t in c[1:]:
        if 'image' in t.tag:
          tmptxt = '![](%s)' % t.attrib['{http://www.w3.org/1999/xlink}href']
          print tmptxt
          outfile_content.append(tmptxt)
        elif t.text:
          #  if t.text[0] == '*':
          #    tmptxt = '    ' + t.text
          tmptxt = t.text
          print t.text
          outfile_content.append(tmptxt)

with open(outfilename, 'w') as outfile:
  outfile.write("\n".join(outfile_content))
