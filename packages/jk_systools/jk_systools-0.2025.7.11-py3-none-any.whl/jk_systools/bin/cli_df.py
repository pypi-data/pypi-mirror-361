#!/usr/bin/python

import typing
import sys
import uuid

import jk_logging
import jk_typing
import jk_console
import jk_sysinfo
import jk_flexdata
# import jk_json

import jk_systools

from ._DataCtx import _DataCtx






#
# IMPLEMENTATION NOTES:
#
# This application iterates over lsblk devices.
# For some reasons some devices might not be listed there.
#
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
			appDescription = "Show disk space of file systems but filter out loopback devices and other less interesting mounts.",
		)

		# ----

		self.argsParser.addDescriptionChapter(None, [
			"This tool shows disk space of file systems but filters out loopback devices and other less interesting mounts.",
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

	# def ____checkAccept(self, data_lsblk:jk_flexdata.FlexObject) -> bool:
	# 	if data_lsblk.mountpoint and data_lsblk.mountpoint.startswith("/snap"):
	# 		return False
	# 
	# 	return True
	# #

	def __collectAllSizeValues(self,
		ctx:_DataCtx,
		outSpaceUsed:typing.List[float],
		outSpaceFree:typing.List[float],
		outSpaceTotal:typing.List[float],
	):
		# if not self.____checkAccept(ctx.data_lsblk):
		# 	return

		if ctx.data_mounts and ctx.data_lsblk.mountpoint:
			data_df_2 = ctx.data_df._get(ctx.data_lsblk.mountpoint)
			if data_df_2:
				outSpaceTotal.append(data_df_2.spaceTotal)
				outSpaceUsed.append(data_df_2.spaceUsed)
				outSpaceFree.append(data_df_2.spaceFree)

		if ctx.data_lsblk.children:
			for c in ctx.data_lsblk.children:
				self.__collectAllSizeValues(ctx.derive(c), outSpaceUsed, outSpaceFree, outSpaceTotal)
	#

	def _setFixedMagnitudes(self, ctx:_DataCtx):
		# spaceUsed:typing.List[float] = []
		# spaceFree:typing.List[float] = []
		# spaceTotal:typing.List[float] = []

		# for _d in ctx.data_lsblk.deviceTree:
		# 	self.__collectAllSizeValues(ctx.derive(_d), spaceUsed, spaceFree, spaceTotal)

		# ctx.magSpaceUsed = jk_sysinfo.value_formatting.getBytesMagnitude(*spaceUsed)
		# ctx.magSpaceFree = jk_sysinfo.value_formatting.getBytesMagnitude(*spaceFree)
		# ctx.magSpaceTotal = jk_sysinfo.value_formatting.getBytesMagnitude(*spaceTotal)

		ctx.magSpaceUsed = "gb"
		ctx.magSpaceFree = "gb"
		ctx.magSpaceTotal = "gb"
	#

	################################################################################################################################

	@jk_typing.checkFunctionSignature()
	def __printDeviceHierarchical(self, ctx:_DataCtx, indent:str=""):
		# if not self.____checkAccept(ctx.data_lsblk):
		# 	return

		s = indent + ctx.data_lsblk.dev

		if ctx.data_lsblk.mountpoint:
			s += " @ "
			s += ctx.data_lsblk.mountpoint
			sAdd = " :: "
		else:
			sAdd = " :: "

		if ctx.data_lsblk.uuid:
			s += sAdd + repr(ctx.data_lsblk.uuid)
			sAdd = " ~ "
		if ctx.data_lsblk.fstype:
			s += sAdd + ctx.data_lsblk.fstype
			sAdd = " ~ "

		print(s)

		indent += "\t"

		if ctx.data_mounts and ctx.data_lsblk.mountpoint:
			data_df_2 = ctx.data_df._get(ctx.data_lsblk.mountpoint)
			#jk_json.prettyPrint(data_mounts._toDict())
			#jk_json.prettyPrint(data_df._toDict())
			if data_df_2:
				print(indent
					+ "total:", jk_sysinfo.formatBytesS(data_df_2.spaceTotal, magOverride=ctx.magSpaceTotal)
					+ ", used:", jk_sysinfo.formatBytesS(data_df_2.spaceUsed, magOverride=ctx.magSpaceUsed)
					+ ", free:", jk_sysinfo.formatBytesS(data_df_2.spaceFree, magOverride=ctx.magSpaceFree)
					+ ", filled:", jk_sysinfo.formatPercentGraphC(data_df_2.spaceUsed, data_df_2.spaceTotal), jk_sysinfo.formatPercent(data_df_2.spaceUsed, data_df_2.spaceTotal)
					)
				#jk_json.prettyPrint(data_df_2._toDict())
			else:
				print(indent + "Not found: " + ctx.data_lsblk.mountpoint)

		if ctx.data_lsblk.children:
			for c in ctx.data_lsblk.children:
				self.__printDeviceHierarchical(ctx.derive(c), indent)
		else:
			print(indent + "n/a")
	#

	@jk_typing.checkFunctionSignature()
	def _printHierarchical(self, ctx:_DataCtx):
		for _d in ctx.data_lsblk.deviceTree:
			self.__printDeviceHierarchical(ctx.derive(_d), "\t")
	#

	#
	# @param		SimpleTable table		(required) Table with the following colums:
	#										* _devPath       : device path
	#										* _mountPoint    : mount path
	#										* _fsLabel       : file system label
	#										* _fstype        : file system type
	#										* _filledChart   : chart
	#										* _filledPerCent : percentage filled
	#										* _spaceFree     : free
	#										* _spaceUsed     : used
	#										* _spaceTotal    : total
	#
	@jk_typing.checkFunctionSignature()
	def __printDeviceFlat(self, ctx:_DataCtx, table:jk_console.SimpleTable):
		# if not self.____checkAccept(ctx.data_lsblk):
		# 	return

		_devPath = ctx.data_lsblk.dev
		_mountPoint = ctx.data_lsblk.mountpoint
		_fsLabel = ctx.data_lsblk.uuid
		try:
			if uuid.UUID(_fsLabel):
				_fsLabel = "(uuid)"
		except:
			pass
		_fstype = ctx.data_lsblk.fstype

		if ctx.data_mounts and ctx.data_lsblk.mountpoint:
			data_df_2 = ctx.data_df._get(ctx.data_lsblk.mountpoint)
			#jk_json.prettyPrint(data_mounts._toDict())
			#jk_json.prettyPrint(data_df._toDict())
			if data_df_2:
				_spaceUsed = str(jk_sysinfo.formatBytes(data_df_2.spaceUsed, magOverride=ctx.magSpaceUsed)[0])
				_spaceFree = str(jk_sysinfo.formatBytes(data_df_2.spaceFree, magOverride=ctx.magSpaceFree)[0])
				_spaceTotal = str(jk_sysinfo.formatBytes(data_df_2.spaceTotal, magOverride=ctx.magSpaceTotal)[0])
				_filledChartC = jk_sysinfo.formatPercentGraphC(data_df_2.spaceUsed, data_df_2.spaceTotal)
				_filledPerCent = jk_sysinfo.formatPercent(data_df_2.spaceUsed, data_df_2.spaceTotal)
				table.addRow(
					_devPath,
					_fsLabel,
					_fstype,
					"{:>5} {}".format(_filledPerCent, _filledChartC),
					_spaceTotal,
					_spaceUsed,
					_spaceFree,
					_mountPoint,
				)[4].textLen = 40

		if ctx.data_lsblk.children:
			for c in ctx.data_lsblk.children:
				self.__printDeviceFlat(ctx.derive(c), table)
	#

	@jk_typing.checkFunctionSignature()
	def _printFlat(self, ctx:_DataCtx):
		self._setFixedMagnitudes(ctx)

		table = jk_console.SimpleTable()
		headerRow = table.addRow(
			"DEVICE_PATH",
			"FS_LABEL",
			"FS_TYPE",
			"FILLED",
			"SIZE_GB",
			"USED_GB",
			"FREE_GB",
			"MOUNT_POINT",
		)
		headerRow.hlineAfterRow = True
		headerRow.halign = jk_console.SimpleTableConstants.HALIGN_LEFT
		headerRow[3].halign = jk_console.SimpleTableConstants.HALIGN_CENTER
		headerRow[4].halign = jk_console.SimpleTableConstants.HALIGN_RIGHT
		headerRow[5].halign = jk_console.SimpleTableConstants.HALIGN_RIGHT
		headerRow[6].halign = jk_console.SimpleTableConstants.HALIGN_RIGHT
		table.column(3).halign = jk_console.SimpleTableConstants.HALIGN_RIGHT
		table.column(4).halign = jk_console.SimpleTableConstants.HALIGN_RIGHT
		table.column(5).halign = jk_console.SimpleTableConstants.HALIGN_RIGHT
		table.column(6).halign = jk_console.SimpleTableConstants.HALIGN_RIGHT

		for _d in ctx.data_lsblk.deviceTree:
			self.__printDeviceFlat(ctx.derive(_d), table)

		if not ctx.bWithFileSystemLabel:
			table.removeColumn(1)

		table.print()
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################
 
	def runImpl(self, ctx:jk_systools.CLIRunCtx) -> int:
		jLsBlk = []
		for jDict in jk_sysinfo.get_lsblk()["deviceTree"]:
			if jDict.get("mountpoint") and jDict["mountpoint"].startswith("/snap"):
				continue
			jLsBlk.append(jDict)
		# jk_json.prettyPrint(jLsBlk)

		ctx = _DataCtx(
			#data_lsblk = jk_flexdata.createFromData(jk_sysinfo.get_lsblk()),
			data_lsblk = jk_flexdata.createFromData({ "deviceTree": jLsBlk }),
			data_mounts = jk_flexdata.createFromData(jk_sysinfo.get_mount()),
			data_df = jk_flexdata.createFromData(jk_sysinfo.get_df()),
		)

		print()
		# self._printHierarchical(ctx)
		self._printFlat(ctx)
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













