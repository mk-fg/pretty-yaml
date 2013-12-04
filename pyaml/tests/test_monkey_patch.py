import pyaml
from unittest import TestCase
import yaml


class TestPyaml(TestCase):
    def test_monkey_patch(self):
    	d = {'a': {'b': 'c'}}

	# test default
	pyaml.dump(d)
	self.assertFalse(pyaml.patched_values['safe'])
	self.assertFalse(pyaml.patched_values['force_embed'])
	self.assertTrue(pyaml.patched_values['patched'])

	self.assertTrue(hasattr(yaml.serializer.Serializer, 'orig_anchor_node'))
	self.assertTrue(hasattr(yaml.serializer.Serializer, 'orig_serialize_node'))
	self.assertTrue(hasattr(yaml.emitter.Emitter, 'orig_expect_block_sequence'))
	self.assertTrue(hasattr(yaml.emitter.Emitter, 'orig_expect_block_sequence_item'))

	# test resetting
	pyaml.dump(d, safe=True)
	self.assertTrue(pyaml.patched_values['safe'])
	self.assertFalse(pyaml.patched_values['force_embed'])
	self.assertTrue(pyaml.patched_values['patched'])

	self.assertFalse(hasattr(yaml.serializer.Serializer, 'orig_anchor_node'))
	self.assertFalse(hasattr(yaml.serializer.Serializer, 'orig_serialize_node'))
	self.assertFalse(hasattr(yaml.emitter.Emitter, 'orig_expect_block_sequence'))
	self.assertFalse(hasattr(yaml.emitter.Emitter, 'orig_expect_block_sequence_item'))

	# test patching again
	pyaml.dump(d, force_embed=True)
	self.assertFalse(pyaml.patched_values['safe'])
	self.assertTrue(pyaml.patched_values['force_embed'])
	self.assertTrue(pyaml.patched_values['patched'])

	self.assertTrue(hasattr(yaml.serializer.Serializer, 'orig_anchor_node'))
	self.assertTrue(hasattr(yaml.serializer.Serializer, 'orig_serialize_node'))
	self.assertTrue(hasattr(yaml.emitter.Emitter, 'orig_expect_block_sequence'))
	self.assertTrue(hasattr(yaml.emitter.Emitter, 'orig_expect_block_sequence_item'))
