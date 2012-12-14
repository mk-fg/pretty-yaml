# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import itertools as it, operator as op, functools as ft
from collections import defaultdict, OrderedDict
import os, sys, yaml


def dump(data, dst=unicode, safe=False, force_embed=False, vspacing=None):
	### WARNING: lots of horrible monkey-patching ahead to produce more readable yaml

	yaml.representer.SafeRepresenter.add_representer(
		defaultdict, yaml.representer.SafeRepresenter.represent_dict )
	yaml.representer.SafeRepresenter.add_representer(
		set, yaml.representer.SafeRepresenter.represent_list )

	def repr_odict(dumper, data):
		value = list()
		node = yaml.nodes.MappingNode(
			'tag:yaml.org,2002:map', value, flow_style=None )
		if dumper.alias_key is not None:
			dumper.represented_objects[dumper.alias_key] = node
		for item_key, item_value in data.viewitems():
			node_key = dumper.represent_data(item_key)
			node_value = dumper.represent_data(item_value)
			value.append((node_key, node_value))
		node.flow_style = False
		return node
	yaml.representer.SafeRepresenter.add_representer(OrderedDict, repr_odict)

	if not safe:
		for str_type in [bytes, unicode]:
			yaml.representer.SafeRepresenter.add_representer(
				str_type, lambda s,o: yaml.representer.ScalarNode(
					'tag:yaml.org,2002:str', unicode(o), style='plain' ) )
		yaml.representer.SafeRepresenter.add_representer(
			type(None), lambda s,o: s.represent_scalar('tag:yaml.org,2002:null', '') )

		yaml.emitter.Emitter.choose_scalar_style =\
			lambda s,func=yaml.emitter.Emitter.choose_scalar_style:\
				func(s) if s.event.style != 'plain' else\
					("'" if ' ' in s.event.value else None)

		def transliterate(string):
			from unidecode import unidecode
			string_new = ''
			for ch in unidecode(string):
				if '0' <= ch <= '9' or 'A' <= ch <= 'Z' or 'a' <= ch <= 'z' or ch in '-_': string_new += ch
				else: string_new += '_'
			return string_new.lower()

		def anchor_node( self, node, hint=list(),
				SequenceNode=yaml.serializer.SequenceNode,
				MappingNode=yaml.serializer.MappingNode ):
			if node in self.anchors:
				if self.anchors[node] is None and not force_embed:
					self.anchors[node] = self.generate_anchor(node)\
						if not hint else '{}'.format(
							transliterate('_-_'.join(map(op.attrgetter('value'), hint))) )
			else:
				self.anchors[node] = None
				if isinstance(node, SequenceNode):
					for item in node.value:
						self.anchor_node(item)
				elif isinstance(node, MappingNode):
					for key, value in node.value:
						self.anchor_node(key)
						self.anchor_node(value, hint=hint+[key])
		yaml.serializer.Serializer.anchor_node = anchor_node

		def serialize_node( self, node, parent, index,
				orig=yaml.serializer.Serializer.serialize_node ):
			if force_embed: self.serialized_nodes.clear()
			return orig(self, node, parent, index)
		yaml.serializer.Serializer.serialize_node = serialize_node

		def expect_block_sequence_item( self, first=False,
				SequenceEndEvent=yaml.emitter.SequenceEndEvent ):
			if not first and isinstance(self.event, SequenceEndEvent):
				self.indent = self.indents.pop()
				self.state = self.states.pop()
			else:
				self.write_indent()
				self.write_indicator('  -', True, indention=True)
				self.states.append(self.expect_block_sequence_item)
				self.expect_node(sequence=True)
		yaml.emitter.Emitter.expect_block_sequence_item = expect_block_sequence_item

	# Post-processing to add some nice'ish spacing for higher levels
	from io import BytesIO
	buff = BytesIO()

	yaml.safe_dump(data, buff, default_flow_style=False, encoding='utf-8')

	if vspacing is not None:
		if isinstance(vspacing, int): vspacing = ['\n']*(vspacing+1)
		buff.seek(0)
		result = list()
		for line in buff:
			level = 0
			line = line.decode('utf-8')
			result.append(line)
			if ':' in line:
				while line.startswith('  '):
					level, line = level + 1, line[2:]
				if len(vspacing) > level and len(result) != 1:
					vspace = vspacing[level]
					result.insert( -1, vspace
						if not isinstance(vspace, int) else '\n'*vspace )
		buff.seek(0), buff.truncate()
		buff.write(''.join(result).encode('utf-8'))

	return buff.getvalue().decode('utf-8')\
		if dst in (str, unicode) else dst.write(buff.getvalue())
