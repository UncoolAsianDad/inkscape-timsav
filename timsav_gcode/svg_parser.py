import inkex
from inkex import Path, bezier, CubicSuperPath
from inkex.transforms import Transform
from lxml import etree
from timsav_gcode import entities


def parse_length_with_units(string):
    """
  Parse an SVG value which may or may not have units attached
  This version is greatly simplified in that it only allows: no units,
  units of px, and units of %.  Everything else, it returns None for.
  There is a more general routine to consider in scour.py if more
  generality is ever needed.
  """
    u = 'px'
    s = string.strip()
    if s[-2:] == 'px':
        s = s[:-2]
    elif s[-2:] == 'in':
        u = 'in'
        s = s[:-2]
    elif s[-2:] == 'mm':
        u = 'mm'
        s = s[:-2]
    elif s[-1:] == '%':
        u = '%'
        s = s[:-1]
    try:
        v = float(s)
    except:
        return None, None
    return v, u


def sub_divide_cubic_path(sp, flat, i=1):
    """
  Break up a bezier curve into smaller curves, each of which
  is approximately a straight line within a given tolerance
  (the "smoothness" defined by [flat]).

  This is a modified version of cspsubdiv.cspsubdiv(). I rewrote the recursive
  call because it caused recursion-depth errors on complicated line segments.
  """

    while True:
        while True:
            if i >= len(sp):
                return

            p0 = sp[i - 1][1]
            p1 = sp[i - 1][2]
            p2 = sp[i][0]
            p3 = sp[i][1]

            b = (p0, p1, p2, p3)

            if bezier.maxdist(b) > flat:
                break

            i += 1

        one, two = bezier.beziersplitatt(b, 0.5)
        sp[i - 1][2] = one[1]
        sp[i][0] = two[2]
        p = [one[2], one[3], two[1]]
        sp[i:1] = [p]


class SvgIgnoredEntity:
    def __init__(self):
        self.tag = None
        self.id = None

    def load(self, node, trans):
        self.tag = node.tag
        self.id = node.get("id")

    def __str__(self):
        return "Ignored '%s' tag" % self.tag

    def get_gcode(self, context):
        context.codes.append("( tag " + str(self.tag) + " id " + str(self.id) + ")")
        context.codes.append("")
        return


class SvgPath(entities.PolyLine):
    def __init__(self):
        super().__init__()
        self.cut_style = 1

    def load(self, node, trans):
        a = node.get('style').split(";")
        d = dict(s.split(':') for s in a)
        if d['stroke'] == "#ff0000":
            self.cut_style = 2
        elif d['stroke'] == "#0000ff":
            self.cut_style = 3
        else:
            pass

        d = node.get('d')
        p = Path(d)
        if len(p) == 0:
            return
        p = CubicSuperPath(p)
        p = p.transform(trans)

        # p is now a list of lists of cubic beziers [ctrl p1, ctrl p2, endpoint]
        # where the start-point is the last point in the previous segment
        self.segments = []
        for sp in p:
            points = []
            sub_divide_cubic_path(sp, 0.2)  # TODO: smoothness preference
            for csp in sp:
                points.append((csp[1][0], csp[1][1]))
            self.segments.append(points)

    def new_path_from_node(self, node):
        new_path = etree.Element(inkex.addNS('path', 'svg'))
        s = node.get('style')
        if s:
            new_path.set('style', s)
        t = node.get('transform')
        if t:
            new_path.set('transform', t)
        return new_path


class SvgRect(SvgPath):
    def load(self, node, trans):
        new_path = self.new_path_from_node(node)
        x = float(node.get('x'))
        y = float(node.get('y'))
        w = float(node.get('width'))
        h = float(node.get('height'))
        a = [['M', [x, y]], ['l', [w, 0]], ['l', [0, h]], ['l', [-w, 0]], ['Z', []]]

        new_path.set('d', str(Path(a)))
        SvgPath.load(self, new_path, trans)


class SvgLine(SvgPath):
    def load(self, node, trans):
        new_path = self.new_path_from_node(node)
        x1 = float(node.get('x1'))
        y1 = float(node.get('y1'))
        x2 = float(node.get('x2'))
        y2 = float(node.get('y2'))
        a = [['M', [x1, y1]], ['L', [x2, y2]]]
        new_path.set('d', str(Path(a)))
        SvgPath.load(self, new_path, trans)


class SvgPolyLine(SvgPath):
    def load(self, node, trans):
        new_path = self.new_path_from_node(node)
        pl = node.get('points', '').strip()
        if pl == '':
            return
        pa = pl.split()
        if not len(pa):
            return

        d = "M " + pa[0]
        for i in range(1, len(pa)):
            d += " L " + pa[i]
        new_path.set('d', d)
        SvgPath.load(self, new_path, trans)


class SvgEllipse(SvgPath):
    def load(self, node, trans):
        rx = float(node.get('rx', '0'))
        ry = float(node.get('ry', '0'))
        SvgPath.load(self, self.make_ellipse_path(rx, ry, node), trans)

    def make_ellipse_path(self, rx, ry, node):
        if rx == 0 or ry == 0:
            return None
        cx = float(node.get('cx', '0'))
        cy = float(node.get('cy', '0'))
        x1 = cx - rx
        x2 = cx + rx
        d = 'M %f,%f ' % (x1, cy) + \
            'A %f,%f ' % (rx, ry) + \
            '0 1 0 %f, %f ' % (x2, cy) + \
            'A %f,%f ' % (rx, ry) + \
            '0 1 0 %f,%f' % (x1, cy)
        new_path = self.new_path_from_node(node)
        new_path.set('d', d)
        return new_path


class SvgCircle(SvgEllipse):
    def load(self, node, trans):
        rx = float(node.get('r', '0'))
        SvgPath.load(self, self.make_ellipse_path(rx, rx, node), trans)


class SvgText(SvgIgnoredEntity):
    def load(self, node, trans):
        inkex.errormsg('Warning: unable to draw text. please convert it to a path first. objID: ' + node.get('id'))
        SvgIgnoredEntity.load(self, node, trans)


class SvgLayerChange:
    def __init__(self, layer_name):
        self.layer_name = layer_name

    def get_gcode(self, context):
        context.codes.append("M01 (Plotting layer '%s')" % self.layer_name)


class SvgParser:
    entity_map = {
        'path': SvgPath,
        'rect': SvgRect,
        'line': SvgLine,
        'polyline': SvgPolyLine,
        'polygon': SvgPolyLine,
        'circle': SvgCircle,
        'ellipse': SvgEllipse,
        'pattern': SvgIgnoredEntity,
        'metadata': SvgIgnoredEntity,
        'defs': SvgIgnoredEntity,
        'eggbot': SvgIgnoredEntity,
        'style': SvgIgnoredEntity,
        ('namedview', 'sodipodi'): SvgIgnoredEntity,
        'text': SvgIgnoredEntity
    }

    def __init__(self, svg):
        self.svg = svg
        self.entities = []
        self.svgHeight = self.get_length('height')

    def parse(self):
        # 0.28222 scale determined by comparing pixels-per-mm in a default Inkscape file.
        # self.svgWidth = self.getLength('width', 354) * 0.28222
        # self.svgHeight = self.getLength('height', 354) * 0.28222
        self.recursively_traverse_svg(self.svg, Transform(((1.0, 0.0, 0), (0.0, -1.0, self.svgHeight))))
        # self.recursivelyTraverseSvg(self.svg)

    def get_length(self, name):
        """
  Get the <svg> attribute with name "name" and default value "default"
  Parse the attribute into a value and associated units.  Then, accept
  no units (''), units of pixels ('px'), and units of percentage ('%').
  """
        svg_string = self.svg.get(name)
        if svg_string:
            v, u = parse_length_with_units(svg_string)
            if not v:
                # Couldn't parse the value
                return None
            elif (u == '') or (u == 'px'):
                return v * 0.26458
            elif u == 'in':
                return v * 25.4
            elif u == 'mm':
                return v
            elif u == '%':
                return None
            else:
                # Unsupported units
                return None
        else:
            # No width specified; assume the default value
            return None

    def recursively_traverse_svg(self, node_list,
                                 trans_current=Transform(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0))),
                                 parent_visibility='visible'):
        """
    Recursively traverse the svg file to plot out all of the
    paths.  The function keeps track of the composite transformation
    that should be applied to each path.

    This function handles path, group, line, rect, polyline, polygon,
    circle, ellipse and use (clone) elements. Notable elements not
    handled include text.  Unhandled elements should be converted to
    paths in Inkscape.

    TODO: There's a lot of inlined code in the eggbot version of this
    that would benefit from the Entities method of dealing with things.
    """
        for node in node_list:
            # Ignore invisible nodes
            v = node.get('visibility', parent_visibility)
            if v == 'inherit':
                v = parent_visibility
            if v == 'hidden' or v == 'collapse':
                pass

            # first apply the current matrix transform to this node's transform

            trans = Transform(node.get("transform"))
            trans_new = trans_current * trans

            if node.tag == inkex.addNS('g', 'svg') or node.tag == 'g':
                if node.get(inkex.addNS('groupmode', 'inkscape')) == 'layer':
                    node.get(inkex.addNS('label', 'inkscape'))

                self.recursively_traverse_svg(node, trans_new, parent_visibility=v)
            elif node.tag == inkex.addNS('use', 'svg') or node.tag == 'use':
                ref_id = node.get(inkex.addNS('href', 'xlink'))
                if ref_id:
                    # [1:] to ignore leading '#' in reference
                    path = '//*[@id="%s"]' % ref_id[1:]
                    ref_node = node.xpath(path)
                    if ref_node:
                        x = float(node.get('x', '0'))
                        y = float(node.get('y', '0'))
                        # Note: the transform has already been applied
                        if (x != 0) or (y != 0):
                            trans_new2 = trans_new * Transform('translate(%f,%f)' % (x, y))
                        else:
                            trans_new2 = trans_new
                        v = node.get('visibility', v)
                        self.recursively_traverse_svg(ref_node, trans_new2, parent_visibility=v)
                    else:
                        pass
                else:
                    pass
            elif not isinstance(node.tag, str):
                pass
            else:
                entity = self.make_entity(node, trans_new)
                if entity is None:
                    inkex.errormsg(
                        'Warning: unable to draw object, please convert it to a path first. objID: ' + node.get('id'))

    def make_entity(self, node, trans):
        for node_type in SvgParser.entity_map.keys():
            tag = node_type
            ns = 'svg'
            if type(tag) is tuple:
                tag = node_type[0]
                ns = node_type[1]
            if node.tag == inkex.addNS(tag, ns) or node.tag == tag:
                constructor = SvgParser.entity_map[node_type]
                entity = constructor()
                entity.load(node, trans)
                self.entities.append(entity)
                return entity
        return None
