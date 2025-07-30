

import typing

import jk_typing
import jk_flexdata
import jk_prettyprintobj





_DataCtx = typing.NewType("_DataCtx", object)

class _DataCtx(jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self,
			data_lsblk:jk_flexdata.FlexObject,
			data_mounts:jk_flexdata.FlexObject,
			data_df:jk_flexdata.FlexObject,
			bWithFileSystemLabel:bool = False,
			magSpaceUsed:str = None,
			magSpaceFree:str = None,
			magSpaceTotal:str = None,
		):

		self.data_lsblk = data_lsblk
		self.data_mounts = data_mounts
		self.data_df = data_df

		self.bWithFileSystemLabel = bWithFileSystemLabel

		self.magSpaceUsed = magSpaceUsed
		self.magSpaceFree = magSpaceFree
		self.magSpaceTotal = magSpaceTotal
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dumpVarNames(self) -> typing.List[str]:
		return [
			"magSpaceUsed",
			"magSpaceFree",
			"magSpaceTotal",
		]
	#
	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def derive(self, data_lsblk:jk_flexdata.FlexObject) -> _DataCtx:
		return _DataCtx(
			data_lsblk,
			self.data_mounts,
			self.data_df,
			self.bWithFileSystemLabel,
			self.magSpaceUsed,
			self.magSpaceFree,
			self.magSpaceTotal,
		)
	#

	################################################################################################################################
	## Public Static Methods
	################################################################################################################################

#




