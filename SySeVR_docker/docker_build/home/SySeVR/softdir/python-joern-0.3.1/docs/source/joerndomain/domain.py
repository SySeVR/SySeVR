from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.util.docfields import Field, GroupedField
from sphinx.util.nodes import make_refnode
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole

class NodeField(GroupedField):

    is_grouped = True
    list_type = nodes.bullet_list

    def __init__(self, name, names=(), label=None, rolename=None):
        Field.__init__(self, name, names, label, True, rolename)
        self.can_collapse = False

    def make_field(self, types, domain, items):
        fieldname = nodes.field_name('', self.label)
        listnode = self.list_type()
        for fieldarg, content in items:
            par = nodes.paragraph()
            par += self.make_xref(self.rolename, domain, fieldarg,
                                  nodes.literal)
            if content and content[0].children:
                par += nodes.Text(' -- ')
                par += content
            listnode += nodes.list_item('', par)
        fieldbody = nodes.field_body('', listnode)
        return nodes.field('', fieldname, fieldbody)

class JoernObj(ObjectDescription):

    def handle_signature(self, sig, signode):
        # add prefix like 'traversal' or 'lookup'
        if self.desc_annotation:
            prefix = '[%s] ' % self.desc_annotation
            signode += addnodes.desc_annotation(prefix, prefix)
        name = sig.split('(')[0]
        signode += addnodes.desc_name(sig, sig)
        return name

    def add_target_and_index(self, name, sig, signode):
        if name not in self.state.document.ids:
            signode['ids'].append(name)
            signode['names'].append(name)
            self.state.document.note_explicit_target(signode)
        objects = self.env.domaindata['joern']['objects']
        objects[name] = (self.env.docname, self.objtype)
        indextext = "%s (%s)" % (name, self.desc_annotation)
        self.indexnode['entries'].append(('single', indextext, name, ''))
        
class JoernTraversal(JoernObj):

    doc_field_types = [
            GroupedField('param', label='Parameter', names=('param',), can_collapse = False),
            Field('in*', label='Ingoing nodes', names=('in*',), has_arg = False),
            NodeField('in', label='Ingoing nodes', names=('in',), rolename = 'ref'),
            Field('out*', label='Outgoing nodes', names=('out*',), has_arg = False),
            NodeField('out', label='Outgoing nodes', names=('out',), rolename = 'ref'),
    ]

    desc_annotation = 'traversal'

class JoernLookup(JoernObj):

    doc_field_types = [
            GroupedField('param', label='Parameter', names=('param',), can_collapse = False),
            Field('out*', label='Outgoing nodes', names=('out*',), has_arg = False),
            NodeField('out', label='Outgoing nodes', names=('out',), rolename = 'ref'),
    ]

    desc_annotation = 'lookup'

class JoernNode(JoernObj):

    doc_field_types = [
            GroupedField('prop', label='Properties', names=('prop',), can_collapse = False),
    ]

    desc_annotation = 'node'

class JoernXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        return title, target

class JoernDomain(Domain):

    label = 'python-joern'
    name = 'joern'

    data_version = 1

    initial_data = {'objects': {}}

    object_types = {
            'traversal': ObjType('traversal', 'traversal'),
            'lookup': ObjType('lookup', 'lookup'),
            'node': ObjType('node', 'node'),
    }

    directives = {
            'traversal': JoernTraversal,
            'lookup': JoernLookup,
            'node': JoernNode,
    }

    roles = {
            'ref': JoernXRefRole(),
    }

    def get_objects(self):
        for name, (docname, objtype) in self.data['objects'].iteritems():
            yield (name, name, objtype, docname, name, 1)

    def resolve_xref(self, env, fromdocname, builder, type, target, node, contnode):
        doc, _ = self.data['objects'].get(target, (None, None))
        if doc:
            return make_refnode(builder, fromdocname, doc, target, contnode, target)
