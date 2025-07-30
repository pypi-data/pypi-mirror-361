class WebRunnerException(Exception):
    pass


class WebRunnerWebDriverNotFoundException(WebRunnerException):
    pass


class WebRunnerOptionsWrongTypeException(WebRunnerException):
    pass


class WebRunnerArgumentWrongTypeException(WebRunnerException):
    pass


class WebRunnerWebDriverIsNoneException(WebRunnerException):
    pass


class WebRunnerExecuteException(WebRunnerException):
    pass


# Json

class WebRunnerJsonException(WebRunnerException):
    pass


class WebRunnerGenerateJsonReportException(WebRunnerJsonException):
    pass


class WebRunnerAssertException(WebRunnerException):
    pass


class WebRunnerHTMLException(WebRunnerException):
    pass


class WebRunnerAddCommandException(WebRunnerException):
    pass


# XML

class XMLException(WebRunnerException):
    pass


class XMLTypeException(XMLException):
    pass


class CallbackExecutorException(WebRunnerException):
    pass
