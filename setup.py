# For compatibility - pyproject.toml should work instead
# ...but it does not atm, so ends up being parsed to setup() values here anyway

import setuptools, re, pathlib as pl

toml_lines = (pl.Path(__file__).parent / 'pyproject.toml').read_text().split('\n')

def toml_lines_rollup(lines, n=0):
	if not lines[n:]: return
	if re.match('\s+', lines[n]):
		return [lines[n].strip(), *(toml_lines_rollup(lines, n+1) or list())]
	if tail := toml_lines_rollup(lines, n+1): lines[n] += ' '.join(tail)
toml_lines_rollup(toml_lines)

def toml_str(key):
	for line, line_next in zip(toml_lines, toml_lines[1:]):
		if (m := re.fullmatch(r'(\w[\w-]+)\s*=\s*(.*?)\s*', line)) and m[1] == key:
			return re.findall(r'"([^"]+?)"', m[2])
	else: raise KeyError(key)

setup_kws = dict(
	((k, k) for k in 'name version license description classifiers'.split()),
	url='Homepage', install_requires='dependencies' )
setup_kws = dict((k1, toml_str(k2)[0]) for k1, k2 in setup_kws.items())

setup_kws['keywords'] = toml_str('keywords')
setup_kws['author'], setup_kws['author_email'] = toml_str('authors')
if fp := getattr(setuptools, 'find_packages', None): setup_kws['packages'] = fp()

setuptools.setup(**setup_kws)
