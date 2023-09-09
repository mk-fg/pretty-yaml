import os, sys, io, enum, unittest, json, collections as cs, functools as ft

import yaml

try: import pyaml.cli
except ImportError:
	sys.path.insert(1, os.path.join(__file__, *['..']*3))
	import pyaml.cli


class test_const(enum.IntEnum):
	dispatch = 2455
	heartbeat = 123

data = dict(
	key='value',
	path='/some/path',
	query_dump=dict(
		key1='тест1',
		key2='тест2',
		key3='тест3',
		последний=None ),
	ids=dict(),
	a=[1,None,'asd', 'не-ascii'], b=3.5, c=None )
data['query_dump_clone'] = data['query_dump']
data['ids']['id в уникоде'] = [4, 5, 6]
data['ids']['id2 в уникоде'] = data['ids']['id в уникоде']
data["'asd'\n!\0\1"] = dict(b=1, a=2)


class CliToolTests(unittest.TestCase):

	def data_hash(self, data):
		return json.dumps(data, sort_keys=True)

	def pyaml_dump_corrupted(self, dump, *args, append=None, **kws):
		out = dump(*args, **kws)
		if append: out += append
		return out

	def test_success(self):
		d, out, err = data.copy(), io.StringIO(), io.StringIO()

		ys = yaml.safe_dump(d)
		pyaml.cli.main( argv=list(),
			stdin=io.StringIO(ys), stdout=out, stderr=err )
		yaml.safe_load(out.getvalue())
		self.assertGreater(len(out.getvalue()), 150)
		self.assertEqual(err.getvalue(), '')

		d.update(
			d=test_const.heartbeat,
			asd=cs.OrderedDict(b=1, a=2) )
		ys = pyaml.dump(d)
		pyaml.cli.main( argv=list(),
			stdin=io.StringIO(ys), stdout=out, stderr=err )
		yaml.safe_load(out.getvalue())
		self.assertGreater(len(out.getvalue()), 150)
		self.assertEqual(err.getvalue(), '')

	def test_load_fail(self):
		d, out, err = data.copy(), io.StringIO(), io.StringIO()
		ys = yaml.safe_dump(d) + '\0asd : fgh : ghj\0'
		with self.assertRaises(yaml.YAMLError):
			pyaml.cli.main( argv=list(),
				stdin=io.StringIO(ys), stdout=out, stderr=err )

	def test_out_broken(self):
		d, out, err = data.copy(), io.StringIO(), io.StringIO()
		pyaml_dump, pyaml.dump = pyaml.dump, ft.partial(
			self.pyaml_dump_corrupted, pyaml.dump, append='\0asd : fgh : ghj\0' )
		try:
			ys = yaml.safe_dump(d)
			pyaml.cli.main( argv=list(),
				stdin=io.StringIO(ys), stdout=out, stderr=err )
			with self.assertRaises(yaml.YAMLError):
				yaml.safe_load(out.getvalue())
			self.assertGreater(len(out.getvalue()), 150)
			self.assertRegex(err.getvalue(), r'^WARNING:')
		finally: pyaml.dump = pyaml_dump

	def test_out_mismatch(self):
		d, out, err = data.copy(), io.StringIO(), io.StringIO()
		pyaml_dump, pyaml.dump = pyaml.dump, ft.partial(
			self.pyaml_dump_corrupted, pyaml.dump, append='\nextra-key: value' )
		try:
			ys = yaml.safe_dump(d)
			pyaml.cli.main( argv=list(),
				stdin=io.StringIO(ys), stdout=out, stderr=err )
			yaml.safe_load(out.getvalue())
			self.assertGreater(len(out.getvalue()), 150)
			self.assertRegex(err.getvalue(), r'^WARNING:')
		finally: pyaml.dump = pyaml_dump

	def test_out_err_nocheck(self):
		d, out, err = data.copy(), io.StringIO(), io.StringIO()
		pyaml_dump, pyaml.dump = pyaml.dump, ft.partial(
			self.pyaml_dump_corrupted, pyaml.dump, append='\0asd : fgh : ghj\0' )
		try:
			ys = yaml.safe_dump(d)
			pyaml.cli.main( argv=['-q'],
				stdin=io.StringIO(ys), stdout=out, stderr=err )
			with self.assertRaises(yaml.YAMLError):
				yaml.safe_load(out.getvalue())
			self.assertGreater(len(out.getvalue()), 150)
			self.assertEqual(err.getvalue(), '')
		finally: pyaml.dump = pyaml_dump


if __name__ == '__main__': unittest.main()
