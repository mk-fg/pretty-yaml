import collections as cs, functools as ft
import os, sys, io, enum, unittest, json, tempfile

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

	def test_replace(self):
		d, out, err = data.copy(), io.StringIO(), io.StringIO()
		sys_out, sys_err = sys.stdout, sys.stderr
		with self.assertRaises(SystemExit):
			sys.stdout, sys.stderr = out, err
			try:
				pyaml.cli.main( argv=['-r'],
					stdin=io.StringIO(), stdout=out, stderr=err )
			finally: sys.stdout, sys.stderr = sys_out, sys_err
		self.assertEqual(out.getvalue(), '')
		self.assertGreater(len(err.getvalue()), 50)
		err.seek(0); err.truncate()

		with tempfile.NamedTemporaryFile(prefix='.pyaml.test.') as tmp:
			d_json, d_yaml = json.dumps(d).encode(), pyaml.dump(d, bytes)
			tmp.write(d_json); tmp.flush()
			os.fchmod(tmp.fileno(), 0o1510)
			stat_tmp = os.fstat(tmp.fileno())

			pyaml.cli.main( argv=['-r', tmp.name],
				stdin=io.StringIO(), stdout=out, stderr=err )
			with open(tmp.name, 'rb') as tmp_new:
				d_new, stat_new = tmp_new.read(), os.fstat(tmp_new.fileno())
			self.assertEqual(out.getvalue(), '')
			self.assertEqual(err.getvalue(), '')

			tmp.seek(0); d_tmp = tmp.read()
			self.assertEqual(d_tmp, d_json)
			self.assertNotEqual(d_tmp, d_new)
			self.assertNotIn(d_json, d_new)
			self.assertEqual(yaml.safe_load(d_new), d)
			self.assertEqual(
				(stat_tmp.st_mode, stat_tmp.st_uid, stat_tmp.st_gid),
				(stat_new.st_mode, stat_new.st_uid, stat_new.st_gid) )

			os.chmod(tmp.name, 0o600)
			with open(tmp.name, 'r+') as tmp_new:
				tmp_new.write('\0asd : fgh : ghj\0')
				tmp_new.seek(0); d_new = tmp_new.read()
			with self.assertRaises(yaml.YAMLError):
				pyaml.cli.main( argv=['-r', tmp.name],
					stdin=io.StringIO(), stdout=out, stderr=err )
			self.assertEqual(out.getvalue(), '')
			self.assertEqual(err.getvalue(), '')
			with open(tmp.name, 'r') as tmp_new:
				tmp_new.seek(0); d_new2 = tmp_new.read()
			self.assertEqual(d_new, d_new2)


if __name__ == '__main__': unittest.main()
