from unittest import runner
from unittest import result

class SerialTestResultHandler(runner.TextTestResult):
  pass


class MasterTestResultHandler(result.TestResult):
  """A test result class that can print formatted text results to a stream.

  Used by TextTestRunner.
  """
  separator1 = '=' * 70
  separator2 = '-' * 70

  def __init__(self, stream, descriptions, verbosity):
    result.TestResult.__init__(self, stream, descriptions, verbosity)
    self.stream = stream
    self.showAll = verbosity > 1
    self.dots = verbosity == 1
    self.descriptions = descriptions

  def getDescription(self, test):
    doc_first_line = test.shortDescription()
    if self.descriptions and doc_first_line:
      return '\n'.join((str(test), doc_first_line))
    else:
      return str(test)

  def startTest(self, test):
    result.TestResult.startTest(self, test)
    if self.showAll:
      self.stream.write(self.getDescription(test))
      self.stream.write(" ... ")
      self.stream.flush()

  def addSuccess(self, test):
    result.TestResult.addSuccess(self, test)
    if self.showAll:
      self.stream.writeln("ok")
    elif self.dots:
      self.stream.write('.')
      self.stream.flush()

  def addError(self, test, err):
    result.TestResult.addError(self, test, err)
    if self.showAll:
      self.stream.writeln("ERROR")
    elif self.dots:
      self.stream.write('E')
      self.stream.flush()

  def addFailure(self, test, err):
    result.TestResult.addFailure(self, test, err)
    if self.showAll:
      self.stream.writeln("FAIL")
    elif self.dots:
      self.stream.write('F')
      self.stream.flush()

  def addSkip(self, test, reason):
    result.TestResult.addSkip(self, test, reason)
    if self.showAll:
      self.stream.writeln("skipped {0!r}".format(reason))
    elif self.dots:
      self.stream.write("s")
      self.stream.flush()

  def addExpectedFailure(self, test, err):
    result.TestResult.addExpectedFailure(self, test, err)
    if self.showAll:
      self.stream.writeln("expected failure")
    elif self.dots:
      self.stream.write("x")
      self.stream.flush()

  def addUnexpectedSuccess(self, test):
    result.TestResult.addUnexpectedSuccess(self, test)
    if self.showAll:
      self.stream.writeln("unexpected success")
    elif self.dots:
      self.stream.write("u")
      self.stream.flush()

  def printErrors(self):
    if self.dots or self.showAll:
      self.stream.writeln()
    self.printErrorList('ERROR', self.errors)
    self.printErrorList('FAIL', self.failures)

  def printErrorList(self, flavour, errors):
    for test, err in errors:
      self.stream.writeln(self.separator1)
      self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
      self.stream.writeln(self.separator2)
      self.stream.writeln("%s" % err)


class WorkerTestResultHandler(result.TestResult):

  def __init__(self, stream, descriptions, verbosity):
    result.TestResult.__init__(self, stream, descriptions, verbosity)
    self.stream = stream
    self.showAll = verbosity > 1
    self.dots = verbosity == 1
    self.descriptions = descriptions

  def getDescription(self, test):
    doc_first_line = test.shortDescription()
    if self.descriptions and doc_first_line:
      return '\n'.join((str(test), doc_first_line))
    else:
      return str(test)

  def startTest(self, test):
    result.TestResult.startTest(self, test)
    if self.showAll:
      self.stream.write(self.getDescription(test))
      self.stream.write(" ... ")
      self.stream.flush()

  def addSuccess(self, test):
    result.TestResult.addSuccess(self, test)
    if self.showAll:
      self.stream.writeln("ok")
    elif self.dots:
      self.stream.write('.')
      self.stream.flush()

  def addError(self, test, err):
    result.TestResult.addError(self, test, err)
    if self.showAll:
      self.stream.writeln("ERROR")
    elif self.dots:
      self.stream.write('E')
      self.stream.flush()

  def addFailure(self, test, err):
    result.TestResult.addFailure(self, test, err)
    if self.showAll:
      self.stream.writeln("FAIL")
    elif self.dots:
      self.stream.write('F')
      self.stream.flush()

  def addSkip(self, test, reason):
    result.TestResult.addSkip(self, test, reason)
    if self.showAll:
      self.stream.writeln("skipped {0!r}".format(reason))
    elif self.dots:
      self.stream.write("s")
      self.stream.flush()

  def addExpectedFailure(self, test, err):
    result.TestResult.addExpectedFailure(self, test, err)
    if self.showAll:
      self.stream.writeln("expected failure")
    elif self.dots:
      self.stream.write("x")
      self.stream.flush()

  def addUnexpectedSuccess(self, test):
    result.TestResult.addUnexpectedSuccess(self, test)
    if self.showAll:
      self.stream.writeln("unexpected success")
    elif self.dots:
      self.stream.write("u")
      self.stream.flush()

  def printErrors(self):
    if self.dots or self.showAll:
      self.stream.writeln()
    self.printErrorList('ERROR', self.errors)
    self.printErrorList('FAIL', self.failures)

  def printErrorList(self, flavour, errors):
    for test, err in errors:
      self.stream.writeln(self.separator1)
      self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
      self.stream.writeln(self.separator2)
      self.stream.writeln("%s" % err)
