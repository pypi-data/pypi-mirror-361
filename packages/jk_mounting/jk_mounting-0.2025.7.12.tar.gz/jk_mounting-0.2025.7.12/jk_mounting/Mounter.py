


import typing
import os
import codecs

import jk_simpleexec


from .MountInfo import MountInfo
from .MountOptions import MountOptions










class Mounter(object):

	################################################################################################################################
	## Constructor Methods
	################################################################################################################################

	def __init__(self):
		# self.__lastRefresh = 0
		self.__mountInfos:typing.List[MountInfo] = None

		self.refresh()
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def __retrieveMountInfos(self) -> typing.List[MountInfo]:
		mountInfos = []
		with codecs.open("/proc/mounts", "r", "utf-8") as f:
			for line in f.readlines():
				line = line[:-1]
				mountInfos.append(MountInfo._parseFromMountLine(line))
		return mountInfos
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def refresh(self):
		# dt = time.time() - self.__lastRefresh
		self.__mountInfos = self.__retrieveMountInfos()
	#

	def getMountInfos(self, fsTypeIncl = None, fsTypeExcl = None, isRegularDevice:bool = None) -> typing.List[MountInfo]:
		if (fsTypeIncl is None) and (fsTypeExcl is None) and (not isRegularDevice):
			return list(self.__mountInfos)

		if isRegularDevice is None:
			pass
		elif isinstance(isRegularDevice, bool):
			pass
		else:
			raise Exception("isRegularDevice is not of type boolean!")

		if fsTypeIncl is None:
			pass
		elif isinstance(fsTypeIncl, str):
			fsTypeIncl = [ fsTypeIncl ]
		elif isinstance(fsTypeIncl, list):
			for fsTypeInclItem in fsTypeIncl:
				assert isinstance(fsTypeInclItem, str)
		else:
			raise Exception("fsTypeIncl is not of type string or string list!")

		if fsTypeExcl is None:
			pass
		elif isinstance(fsTypeExcl, str):
			fsTypeExcl = [ fsTypeExcl ]
		elif isinstance(fsTypeExcl, list):
			for fsTypeExclItem in fsTypeExcl:
				assert isinstance(fsTypeExclItem, str)
		else:
			raise Exception("fsTypeExcl is not of type string or string list!")

		ret = []
		for mi in self.__mountInfos:
			if isRegularDevice is not None:
				if isRegularDevice:
					if not mi.isRegularDevice:
						continue
				else:
					if mi.isRegularDevice:
						continue
			if fsTypeExcl is not None:
				if mi.fsType in fsTypeExcl:
					continue
			if fsTypeIncl is not None:
				if mi.fsType not in fsTypeIncl:
					continue
			ret.append(mi)
		return ret
	#

	def getMountInfos2(self,
			fsTypeIncl:typing.Union[str,typing.List[str],typing.Tuple[str],None] = None,
			fsTypeExcl:typing.Union[str,typing.List[str],typing.Tuple[str],None] = None,
			isRegularDevice:typing.Union[bool,None] = None,
			isNetworkDevice:typing.Union[bool,None] = None,
			isSnapDevice:typing.Union[bool,None] = False,
			isSysOSDevice:typing.Union[bool,None] = False,
			isFuseDevice:typing.Union[bool,None] = None,
		) -> typing.List[MountInfo]:

		#if (fsTypeIncl is None) and (fsTypeExcl is None) and (isRegularDevice is None) and (isNetworkDevice is None) and (isSnapDevice is None) and (isSysOSDevice is None):
		#	return list(self.__mountInfos)

		# verify arguments

		if isRegularDevice is not None:
			if not isinstance(isRegularDevice, bool):
				raise Exception("isRegularDevice is not of type boolean!")

		if isNetworkDevice is not None:
			if not isinstance(isNetworkDevice, bool):
				raise Exception("isNetworkDevice is not of type boolean!")

		if isSnapDevice is not None:
			if not isinstance(isSnapDevice, bool):
				raise Exception("isSnapDevice is not of type boolean!")

		if isSysOSDevice is not None:
			if not isinstance(isSysOSDevice, bool):
				raise Exception("isSnapDevice is not of type boolean!")

		if isFuseDevice is not None:
			if not isinstance(isFuseDevice, bool):
				raise Exception("isFuseDevice is not of type boolean!")

		if fsTypeIncl is not None:
			if isinstance(fsTypeIncl, str):
				fsTypeIncl = [ fsTypeIncl ]
			elif isinstance(fsTypeIncl, (list,tuple)):
				for fsTypeInclItem in fsTypeIncl:
					assert isinstance(fsTypeInclItem, str)
			else:
				raise Exception("fsTypeIncl is not of type string or string list!")

		if fsTypeExcl is not None:
			if isinstance(fsTypeExcl, str):
				fsTypeExcl = [ fsTypeExcl ]
			elif isinstance(fsTypeExcl, (list,tuple)):
				for fsTypeExclItem in fsTypeExcl:
					assert isinstance(fsTypeExclItem, str)
			else:
				raise Exception("fsTypeExcl is not of type string or string list!")

		# ----

		ret = []
		for mi in self.__mountInfos:
			bRejectAccept = [ None, None, None, True ]

			if isRegularDevice is not None:
				if mi.isRegularDevice:
					bRejectAccept[1] = isRegularDevice

			if isNetworkDevice is not None:
				if mi.isNetworkDevice:
					bRejectAccept[1] = isNetworkDevice

			if isSnapDevice is not None:
				if mi.isSnapDevice:
					bRejectAccept[1] = isSnapDevice

			if isSysOSDevice is not None:
				if mi.isSysOSDevice:
					bRejectAccept[1] = isSysOSDevice

			if isFuseDevice is not None:
				if mi.isFuseDevice:
					bRejectAccept[1] = isFuseDevice

			if fsTypeExcl is not None:
				if mi.fsType in fsTypeExcl:
					bRejectAccept[0] = False

			if fsTypeIncl is not None:
				if mi.fsType not in fsTypeIncl:
					bRejectAccept[2] = True

			# print(mi.mountPoint, mi.device, bRejectAccept)

			# process flags
			for b in bRejectAccept:
				if b is True:
					ret.append(mi)
					break
				elif b is False:
					break

		return ret
	#

	#
	# Identifies the mount point a file or directory resides on.
	#
	def getMountInfoByFilePath(self, somePath:str, raiseException:bool = False) -> typing.Union[MountInfo,None]:
		assert isinstance(somePath, str)
		assert isinstance(raiseException, bool)

		somePath = os.path.realpath(os.path.abspath(somePath))

		mountPointPaths = []
		devMap = {}
		for mi in self.getMountInfos():
			assert isinstance(mi, MountInfo)
			devMap[mi.mountPoint] = mi
			mountPointPaths.append(mi.mountPoint)

		mountPointPaths = sorted(mountPointPaths, reverse=True)
		for p in mountPointPaths:
			if p == somePath:
				return devMap[p]
		for p in mountPointPaths:
			p2 = (p + "/") if (len(p) > 1) else p
			if somePath.startswith(p2):
				return devMap[p]

		if raiseException:
			raise Exception("No file system for: " + repr(somePath))
		else:
			return None
	#

	#
	# Identifies the mount point a file or directory resides on.
	#
	def getMountInfoByMountPoint(self, mountPointPath:str, raiseException:bool = False) -> typing.Union[MountInfo,None]:
		assert isinstance(mountPointPath, str)
		assert os.path.isabs(mountPointPath)
		assert isinstance(raiseException, bool)

		mountPointPaths = []
		devMap = {}
		for mi in self.getMountInfos():		# TODO: improve performance by removing duplicate loop
			assert isinstance(mi, MountInfo)
			devMap[mi.mountPoint] = mi
			mountPointPaths.append(mi.mountPoint)

		mountPointPaths = sorted(mountPointPaths, reverse=True)
		for p in mountPointPaths:
			if p == mountPointPath:
				return devMap[p]

		if raiseException:
			raise Exception("No file system for: " + repr(mountPointPath))
		else:
			return None
	#

	#
	# Identifies the mount point a file or directory resides on.
	#
	def getMountInfo(self, device:str = None, fsType:str = None, mountPoint:str = None, raiseException:bool = False) -> typing.Union[MountInfo,None]:
		if device is not None:
			assert isinstance(device, str)
		if fsType is not None:
			assert isinstance(fsType, str)
		if mountPoint is not None:
			assert isinstance(mountPoint, str)
		if (mountPoint is None) and (device is None) and (fsType is None):
			raise Exception("No filter specified!")
		assert isinstance(raiseException, bool)

		for mi in self.getMountInfos():		# TODO: improve performance by removing duplicate loop
			#print("x", repr(mi.mountPoint), repr(mi.device), repr(device))
			bAccept = True
			if device is not None:
				if (device is not None) and (mi.device != device):
					bAccept = False
				elif (fsType is not None) and (mi.fsType != fsType):
					bAccept = False
				elif (mountPoint is not None) and (mi.mountPoint != mountPoint):
					bAccept = False
			if bAccept:
				return mi

		if raiseException:
			raise Exception("No mount entry found.")
		else:
			return None
	#

	def dump(self, prefix:str = ""):
		if prefix is None:
			prefix = ""
		print("mount infos:")
		for m in self.__mountInfos:
			m.dump(prefix + "\t")
	#

	def isMounted(self, path):
		for mi in self.__mountInfos:
			if mi.device == path:
				return True
			if mi.mountPoint == path:
				return True
		return False
	#

	#
	# Mount a device.
	# This method internally calls "/bin/mount".
	#
	# @param	str device						The device to mount. Specify the device path here.
	# @param	str mountPoint					The location where to mount the specified device. Specify an existing empty directory here.
	# @param	mixed options					Mount options. Specify a mount options string here as you would if you invoke "mount" directly,
	#											a list of strings to concatenate or a dictionary with key-value pairs containing all mount options.
	#											Additionally you can specify a <c>MountOptions</c> object, which then get's converted to a suitable
	#											option string automatically.
	# @param	bool raiseExceptionIfMounted	Before mounting a device a check is performed if the device is already mounted (by invoking
	#											<c>self.isMounted(...)</c>. If <c>True</c> is specified here an exception is raised if
	#											the device in question is already mounted (or the path in question is already used as a
	#											mount point).
	#
	def mount(self, device:str, mountPoint:str, options = None, raiseExceptionIfMounted = True) -> bool:
		assert isinstance(device, str)
		assert isinstance(mountPoint, str)
		assert isinstance(options, (type(None), str, list, dict, MountOptions))
		assert isinstance(raiseExceptionIfMounted, bool)

		if self.isMounted(device):
			if raiseExceptionIfMounted:
				raise Exception("Device " + device + " already mounted!")
			else:
				return False

		if self.isMounted(mountPoint):
			if raiseExceptionIfMounted:
				raise Exception("Path " + mountPoint + " already mounted!")
			else:
				return False

		if isinstance(options, MountOptions):
			options = str(options)
		elif isinstance(options, list):
			s = ""
			bNeedsComma = False
			for option in options:
				if bNeedsComma:
					s += ","
				else:
					bNeedsComma = True
				s += option
			options = s
		elif isinstance(options, dict):
			s = ""
			bNeedsComma = False
			for optionName in options:
				optionValue = options[optionName]
				if bNeedsComma:
					s += ","
				else:
					bNeedsComma = True
				s += optionName
				if optionValue is not None:
					s += "=" + optionValue
			options = s

		args = []
		if (options is not None) and (len(options) > 0):
			args.append("-o")
			args.append(options)
		args.append(device)
		args.append(mountPoint)

		result = jk_simpleexec.invokeCmd("/bin/mount", args)
		if len(result.stdErrLines) > 0:
			for s in result.stdErrLines:
				if s.find(": WARNING:") >= 0:
					continue
				else:
					raise Exception(s)
		if result.returnCode != 0:
			raise Exception("Failed to mount " + device + " at " + mountPoint + "!")
		return True
	#

	#
	# Unmount a device.
	# This method internally calls "/bin/umount".
	#
	def unmount(self, deviceOrMountPoint:str, raiseExceptionIfNotMounted = True) -> bool:
		assert isinstance(deviceOrMountPoint, str)
		assert isinstance(raiseExceptionIfNotMounted, bool)

		if not self.isMounted(deviceOrMountPoint):
			if raiseExceptionIfNotMounted:
				raise Exception(deviceOrMountPoint + " is not mounted!")

		result = jk_simpleexec.invokeCmd("/bin/umount", [ deviceOrMountPoint ])
		if len(result.stdErrLines) > 0:
			for s in result.stdErrLines:
				if s.find(": WARNING:") >= 0:
					continue
				else:
					raise Exception(s)
		if result.returnCode != 0:
			raise Exception("Failed to unmount " + deviceOrMountPoint + "!")
		return True
	#

	#
	# Unmount a device.
	# This method internally calls "/bin/fusermount".
	#
	def userUMount(self, deviceOrMountPoint:str, raiseExceptionIfNotMounted = True) -> bool:
		assert isinstance(deviceOrMountPoint, str)
		assert isinstance(raiseExceptionIfNotMounted, bool)

		if not os.path.isfile("/bin/fusermount"):
			raise Exception("Not installed: fusermount")

		if not self.isMounted(deviceOrMountPoint):
			if raiseExceptionIfNotMounted:
				raise Exception(deviceOrMountPoint + " is not mounted!")

		result = jk_simpleexec.invokeCmd("/bin/fusermount", [ "-u", deviceOrMountPoint ])
		if len(result.stdErrLines) > 0:
			for s in result.stdErrLines:
				if s.find(": WARNING:") >= 0:
					continue
				else:
					raise Exception(s)
		if result.returnCode != 0:
			raise Exception("Failed to unmount " + deviceOrMountPoint + "!")
		return True
	#

#






















