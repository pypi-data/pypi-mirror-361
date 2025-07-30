
__all__ = ( "AbstractNoCmdCLIApp" )

import os
import sys
import typing

import jk_typing
import jk_logging
import jk_version
import jk_argparsing

from .AbstractCLICmd import AbstractCLICmd
from .AppRuntime import AppRuntime
from .CLIRunCtx import CLIRunCtx
from .IExitCodes import IExitCodes



_OPT_VERSION_ID = "__showVersion"
_OPT_VERBOSE_ID = "__bVerbose"
_OPT_USE_COLOR_ID = "__bUseColor"
_OPT_RUN_HELP_ID = "__runHelp"







class AbstractMultiCmdCLIApp(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self,
			appFilePath:str,
			appDescription:str,
			appVersion:typing.Union[jk_version.Version,str],
			appCLICommands:typing.List[AbstractCLICmd] = [],
			appRuntimeType:type = AppRuntime,
		):

		assert os.path.isabs(appFilePath)
		assert appDescription

		# ----

		if isinstance(appVersion, str):
			appVersion = jk_version.Version(appVersion)

		# ----

		self.__appVersion = appVersion
		self.__appFilePath = appFilePath
		self.__appFileDirPath = os.path.dirname(appFilePath)
		self.__appFileName = os.path.basename(appFilePath)
		self.__appRuntimeType = appRuntimeType
		self.__appDescription = appDescription

		self.__cliCmdList = appCLICommands

		self.__cliCmdMap = {
			x.cliCmdName:x for x in appCLICommands
		}

		self.__ap = jk_argparsing.ArgsParser(self.__appFileName, appDescription)
		self.__ap.optionDataDefaults.set(_OPT_RUN_HELP_ID, False)
		self.__ap.optionDataDefaults.set(_OPT_USE_COLOR_ID, self.__checkTerminalColorSupport())
		self.__ap.optionDataDefaults.set(_OPT_VERBOSE_ID, False)
		self.__ap.optionDataDefaults.set(_OPT_VERSION_ID, False)

		self.__ap.createOption("h", "help", "Display this help page.").onOption = \
			lambda argOption, argOptionArguments, parsedArgs: \
				parsedArgs.optionData.set(_OPT_RUN_HELP_ID, True)

		self.__ap.createOption(None, "version", "Show the version number).").onOption = \
			lambda argOption, argOptionArguments, parsedArgs: \
				parsedArgs.optionData.set(_OPT_VERSION_ID, True)

		self.__ap.createOption("v", "verbose", "Enable more verbose output.").onOption = \
			lambda argOption, argOptionArguments, parsedArgs: \
				parsedArgs.optionData.set(_OPT_VERBOSE_ID, True)

		self.__ap.createOption(None, "color", "Enforce using color in output. This option overrides the automatic detection of the terminal's color support.").onOption = \
			lambda argOption, argOptionArguments, parsedArgs: \
				parsedArgs.optionData.set(_OPT_USE_COLOR_ID, 1)

		self.__ap.createOption(None, "no-color", "Enforce using no colors in output. This option overrides the automatic detection of the terminal's color support.").onOption = \
			lambda argOption, argOptionArguments, parsedArgs: \
				parsedArgs.optionData.set(_OPT_USE_COLOR_ID, -1)

		self.__ap.createReturnCode(IExitCodes.SUCCESS, "Success.")
		self.__ap.createReturnCode(IExitCodes.ERR_GENERAL, "An error occured.")
		self.__ap.createReturnCode(IExitCodes.HELP_TEXT_OR_VERSION, "The help text is printed.")
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def argsParser(self) -> jk_argparsing.ArgsParser:
		return self.__ap
	#

	@property
	def appDescription(self) -> str:
		return self.__appDescription
	#

	@property
	def cliCmdList(self) -> typing.List[AbstractCLICmd]:
		return self.__cliCmdList
	#

	@property
	def appFilePath(self) -> str:
		return self.__appFilePath
	#

	@property
	def appFileDirPath(self) -> str:
		return self.__appFileDirPath
	#

	@property
	def appFileName(self) -> str:
		return self.__appFileName
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def __checkTerminalColorSupport(self) -> bool:
		platform = sys.platform
		sEnvTERM = os.environ.get("TERM")
		if sEnvTERM and (sEnvTERM in [ "xterm-256color", "xterm-16color", "xterm-color" ]):
			return True
		bIsSupportedPlatform = (platform != "Pocket PC") and (platform != "win32") or ("ANSICON" in os.environ)
		if not bIsSupportedPlatform:
			return False
		return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
	#

	@jk_typing.checkFunctionSignature()
	def __createConsoleLogger(self, bColor:bool) -> jk_logging.AbstractLogger:
		log = jk_logging.MulticastLogger.create()
		if bColor:
			log.addLogger(
				jk_logging.ConsoleLogger.create(logMsgFormatter=jk_logging.COLOR_LOG_MESSAGE_FORMATTER)
			)

			# NOTE: some terminals require this to support color output ...
			if os.name == 'nt':
				os.system("color")
		else:
			log.addLogger(
				jk_logging.ConsoleLogger.create(logMsgFormatter=jk_logging.DEFAULT_LOG_MESSAGE_FORMATTER)
			)
		return log
	#

	@jk_typing.checkFunctionSignature()
	def __replaceDefaultConsoleLogger(self, log:jk_logging.MulticastLogger, bColor:bool):
		log.removeAllLoggers()

		if bColor:
			log.addLogger(
				jk_logging.ConsoleLogger.create(logMsgFormatter=jk_logging.COLOR_LOG_MESSAGE_FORMATTER)
			)

			# NOTE: some terminals require this to support color output ...
			if os.name == 'nt':
				os.system("color")

		else:
			log.addLogger(
				jk_logging.ConsoleLogger.create(logMsgFormatter=jk_logging.DEFAULT_LOG_MESSAGE_FORMATTER)
			)

		return log
	#

	def __runCmdCatchException(self, appRuntime, cmdArgs:typing.Union[tuple,list], cmd:AbstractCLICmd, log:jk_logging.AbstractLogger) -> int:
		try:
			ret = cmd.execute(appRuntime, *cmdArgs, log)
			if ret is not None:
				assert isinstance(ret, int)
				return ret
			return 0
		except jk_logging.ExceptionInChildContextException as ee:
			return IExitCodes.ERR_GENERAL
		except Exception as ee:
			log.error(ee)
			return IExitCodes.ERR_GENERAL
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def showHelp(self, ctx:CLIRunCtx) -> int:
		self.__ap.showHelp(ctx.parsedArgs.optionData[_OPT_USE_COLOR_ID] > 0)
		return IExitCodes.HELP_TEXT_OR_VERSION
	#

	@jk_typing.checkFunctionSignature()
	def runImpl(self, ctx:CLIRunCtx) -> int:
		if not ctx.parsedArgs.programArgs:
			return self.showHelp(ctx)

		for cmdName, cmdArgs in ctx.parsedArgs.parseCommands():
			_cmd = self.__cliCmdMap.get(cmdName)
			if _cmd is None:
				raise Exception("No such command: " + _cmd)
			else:
				with ctx.log.descend("Command " + cmdName) as log2:
					ret = self.__runCmdCatchException(ctx.appRuntime, cmdArgs, _cmd, log2)
					assert isinstance(ret, int)
					if ret == 0:
						log2.success("Success.")
					else:
						log2.error("Terminating with error.")
					return ret

		ctx.log.success("Success.")
		return 0
	#

	def run(self) -> int:
		for cmd in self.__cliCmdList:
			assert isinstance(cmd, AbstractCLICmd)
			cmd.registerCLICommand(self.__ap)

		with self.__createConsoleLogger(self.__ap.optionDataDefaults[_OPT_USE_COLOR_ID] > 0) as log:
			parsedArgs = self.__ap.parse()
			bVerbose = parsedArgs.optionData[_OPT_VERBOSE_ID]
			bShowVersion = parsedArgs.optionData[_OPT_VERSION_ID]
			bUseColor = parsedArgs.optionData[_OPT_USE_COLOR_ID] > 0
			#parsedArgs.dump()

			if parsedArgs.optionData[_OPT_USE_COLOR_ID] <= 0:
				self.__replaceDefaultConsoleLogger(log, False)
			elif parsedArgs.optionData[_OPT_USE_COLOR_ID] > 0:
				self.__replaceDefaultConsoleLogger(log, True)

			if bShowVersion:
				print()
				print("{} version: {}".format(self.__ap.appName, self.__appVersion))
				print()
				return IExitCodes.HELP_TEXT_OR_VERSION

			if parsedArgs.optionData[_OPT_RUN_HELP_ID]:
				return self.showHelp(CLIRunCtx(parsedArgs, None, log))

			with log.descend("Initializing ...", logLevel=jk_logging.EnumLogLevel.NOTICE) as log2:
				# TODO: pack the following handling of log messages into an own wrapper
				blog = jk_logging.BufferLogger.create()
				dlog = jk_logging.DetectionLogger.create(blog)
				appRuntime = None
				try:
					# instantiate app runtime object
					appRuntime = self.__appRuntimeType(bVerbose, bUseColor, parsedArgs.optionData)
					# NOTE: created instance must be derived from AppRuntime
					assert isinstance(appRuntime, AppRuntime)
				except:
					blog.forwardTo(log2)
					raise
				if dlog.stats.hasAtLeastWarning or bVerbose:
					blog.forwardTo(log2)
				if not appRuntime:
					return IExitCodes.ERR_INTERNAL

			ret = self.runImpl(CLIRunCtx(parsedArgs, appRuntime, log))
			assert isinstance(ret, int)
			return ret
	#

#



