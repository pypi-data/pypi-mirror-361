

import os
import typing

import jk_typing
import jk_prettyprintobj





class AppRuntime(jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self,
			bVerbose:bool,
			bUseColor:bool,
			appOptions:typing.Dict[str,typing.Any],
		):

		self.__bVerbose = bVerbose
		self.__bUseColor = bUseColor
		self.__appOptions = appOptions
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	#
	# This property returns True if verbose is enabled.
	#
	@property
	def bVerbose(self) -> bool:
		return self.__bVerbose
	#

	@property
	def bUseColor(self) -> bool:
		return self.__bUseColor
	#

	@property
	def appOptions(self) -> typing.Dict[str,typing.Any]:
		# TODO: provide a read only version of the dict
		return self.__appOptions
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dumpVarNames(self) -> list:
		return [
			"bVerbose",
			"bUseColor",
			"appOptions",
		]
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

#










