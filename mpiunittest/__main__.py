import sys

import mpiunittest

if __name__ == '__main__':
  test_program = mpiunittest.get_test_program()
  test_program.progName = 'mpiunittest'
  test_program.parse_args(sys.argv)
  test_program.run_tests()

