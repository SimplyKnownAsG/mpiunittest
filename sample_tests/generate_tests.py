
def write_suite(number):
  with open('test_suite{}.py'.format(number), 'w') as stream:
    stream.write('import unittest\n')
    stream.write('import time\n')
    stream.write('\n')
    for ss in range(number):
      stream.write('class Suite{}_{}Tests(unittest.TestCase):\n'
                   .format(number, ss))
      stream.write('\n')
      for tt in range(number):
        stream.write('  def test_{}(self):\n'.format(tt))
        stream.write('    time.sleep({:.1f})\n'.format(tt / float(number)))
        stream.write('    self.assertEqual({0}, {0})\n'.format(tt))
        stream.write('\n')

if __name__ == '__main__':
  for nn in range(10):
    write_suite(nn)
