#!/usr/bin/python

import os
import typing
import sys

import jk_logging
import jk_typing
import jk_console
import jk_mounting

import jk_systools








class MainApp(jk_systools.AbstractMultiCmdCLIApp):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self):

		super().__init__(
			appFilePath = __file__,
			appVersion = jk_systools.__version__,
			appDescription = "Show mounted file systems but filter out loopback devices and other less interesting mounts.",
		)

		# ----

		self.argsParser.addDescriptionChapter(None, [
			"This tool shows mounted file systems but filters out loopback devices and other less interesting mounts.",
		])

		# ----

		# self.argsParser.createReturnCode(1, "An error occurred.")
		self.argsParser.createAuthor("Jürgen Knauth", "pubsrc@binary-overflow.de")
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################
 
	def runImpl(self, ctx:jk_systools.CLIRunCtx) -> int:
		mounter = jk_mounting.Mounter()

		interesting:typing.List[jk_mounting.MountInfo] = []
		for mi in mounter.getMountInfos2(isRegularDevice=True, isNetworkDevice=True, isFuseDevice=True):
			interesting.append(mi)
		interesting.sort(key=lambda x: x.mountPoint)

		table = jk_console.SimpleTable()
		headRow = table.addRow("MOUNT_POINT", "DEVICE_PATH", "FS_TYPE", "MODE")
		headRow.hlineAfterRow = True

		for mi in interesting:
			assert isinstance(mi, jk_mounting.MountInfo)
			table.addRow(mi.mountPoint, mi.device, mi.fsType, "r" if mi.isReadOnly else "rw")

		print()
		table.print()
		print()

		return jk_systools.IExitCodes.SUCCESS
	#

#








def main():
	appExitCode = jk_systools.IExitCodes.ERR_INTERNAL
	try:
		appExitCode = MainApp().run()
	except jk_logging.ExceptionInChildContextException as ee:
		#print(repr(ee.originalExeption))
		pass

	sys.exit(appExitCode)
#













