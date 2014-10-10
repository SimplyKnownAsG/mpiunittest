import mpiunittest

if __name__ == '__main__':
  test_program = mpiunittest.get_test_program()
  test_program.parse_args()
  test_program.progName = 'mpiunittest'
  test_program.run_tests()

