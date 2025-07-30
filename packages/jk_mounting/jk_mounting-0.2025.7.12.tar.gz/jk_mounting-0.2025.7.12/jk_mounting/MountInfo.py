

import typing

import jk_prettyprintobj






MountInfo = typing.NewType("MountInfo", object)

#
# This class represents information of a mount point as returend by the Linux system tool "mount".
#
class MountInfo(jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constructor Methods
	################################################################################################################################

	def __init__(self, device:str, mountPoint:str, fsType:str, options:dict):
		self.__device = device
		self.__mountPoint = mountPoint
		self.__fsType = fsType
		self.__options = options
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	#
	# Is this a regular device like "/dev/sda1" or "/dev/nvme0n1p3" or is this something like "proc" or "udev"?
	#
	@property
	def isRegularDevice(self) -> bool:
		return self.__device.startswith("/") and not self.__mountPoint.startswith("/snap/")
	#

	@property
	def isSnapDevice(self) -> bool:
		return self.__mountPoint.startswith("/snap/")
	#

	@property
	def isSysOSDevice(self) -> bool:
		return self.__mountPoint.startswith("/proc/") \
			or self.__mountPoint.startswith("/sys/") \
			or self.__mountPoint.startswith("/snap/") \
			or self.__mountPoint.startswith("/run/") \
			or self.__mountPoint.startswith("/dev/") \
			or (self.__mountPoint == "/dev") \
			or (self.__mountPoint == "/proc") \
			or (self.__mountPoint == "/sys") \
			or (self.__mountPoint == "/run")
	#

	@property
	def isFuseDevice(self) -> bool:
		return self.__fsType.startswith("fuse") and not self.isSysOSDevice
	#

	#
	# This kind of detection might not be too reliable.
	#
	@property
	def isNetworkDevice(self) -> bool:
		return (self.__device.find(":/") > 0) # or self.__fsType.startswith("fuse.")
	#

	#
	# This kind of detection might not be too reliable.
	#
	@property
	def isMTPDevice(self) -> bool:
		return self.__device == "jmtpfs"
	#

	@property
	def isReadOnly(self) -> bool:
		return "ro" in self.__options
	#

	#
	# The device. This is an absolute path such as "/dev/sda" or "/dev/nvme0n1p3" or some other identifier such as "proc" or "udev".
	#
	@property
	def device(self) -> str:
		return self.__device
	#

	#
	# The mount point. This is something like "/", "/sys/fs/cgroup/perf_event" or "/snap/core/8213".
	#
	@property
	def mountPoint(self) -> str:
		return self.__mountPoint
	#

	#
	# The type of the file system used. Example values:
	#
	# * (regular files systems)
	# 		* vfat
	# 		* ext4
	# * (fuse)
	# 		* fuse
	# 		* fuse.Locked(fs.rootNode)
	# 		* fuse.gvfsd-fuse
	# 		* fuseblk
	# 		* fusectl
	# * (other)
	# 		* autofs
	# 		* binfmt_misc
	# 		* bpf
	# 		* cgroup
	# 		* cgroup2
	# 		* configfs
	# 		* debugfs
	# 		* devpts
	# 		* devtmpfs
	# 		* efivarfs
	# 		* hugetlbfs
	# 		* mqueue
	# 		* nsfs
	# 		* proc
	# 		* pstore
	# 		* rpc_pipefs
	# 		* securityfs
	# 		* squashfs
	# 		* sysfs
	# 		* tmpfs
	# 		* tracefs
	#
	@property
	def fsType(self) -> str:
		return self.__fsType
	#

	#
	# THe mount options. This is something like "rw,nodev,relatime,fd=32,pgrp=1,timeout=0,minproto=5,maxproto=5,direct,pipe_ino=1140" converted to a dictionary.
	# The dictionary keys are the individual options, the dictionary values the values of the mount options. If no values are assigned for a key `None` is used for the value.
	#
	@property
	def options(self) -> dict:
		return self.__options
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dumpVarNames(self) -> list:
		return [
			"device",
			"mountPoint",
			"fsType",
			"options",
			"device",
			"isRegularDevice",
			"isNetworkDevice",
			"isSnapDevice",
			"isMTPDevice",
			"isFuseDevice",
			"isReadOnly",
		]
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __eq__(self, other):
		if isinstance(other, MountInfo):
			return self.__mountPoint == other.__mountPoint
		elif isinstance(other, str):
			return self.__mountPoint == other
		else:
			raise TypeError()
	#

	def __ne__(self, other):
		if isinstance(other, MountInfo):
			return self.__mountPoint != other.__mountPoint
		elif isinstance(other, str):
			return self.__mountPoint != other
		else:
			raise TypeError()
	#

	def toJSON(self):
		return {
			"device": self.__device,
			"mountPoint": self.__mountPoint,
			"fsType": self.__fsType,
			"options": self.__options,
			"isRegularDevice": self.isRegularDevice,
			"isNetworkDevice": self.isNetworkDevice,
			"isSnapDevice": self.isSnapDevice,
			"isMTPDevice": self.isMTPDevice,
			"isSysOSDevice": self.isSysOSDevice,
			"isFuseDevice": self.isFuseDevice,
			"isReadOnly": self.isReadOnly,
		}
	#

	def __str__(self):
		s = [
			"MountInfo(device=",
			self.__device,
			", mountPoint=",
			self.__mountPoint,
			", fsType=",
			self.__fsType,
		]
		if self.isRegularDevice:
			s.append(", isRegularDevice")
		if self.isNetworkDevice:
			s.append(", isNetworkDevice")
		if self.isSnapDevice:
			s.append(", isSnapDevice")
		if self.isMTPDevice:
			s.append(", isMTPDevice")
		if self.isSysOSDevice:
			s.append(", isSysOSDevice")
		if self.isFuseDevice:
			s.append(", isFuseDevice")
		if self.isReadOnly:
			s.append(", isReadOnly")
		s.append(")")
		return "".join(s)
	#

	def __repr__(self):
		return self.__str__()
	#

	def __hash__(self):
		return self.__mountPoint.__hash__()
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	#
	# This method is invoked by `Mounter` to parse a mount information text line.
	#
	@staticmethod
	def _parseFromMountLine(line) -> MountInfo:
		assert isinstance(line, str)

		# print(":: " + line)

		elements = line.split(' ')
		while len(elements) > 6:
			elements[1] = elements[1] + elements[2]
			del elements[2]
		options = dict()
		for optionLine in elements[3].split(","):
			pos = optionLine.find("=")
			if pos < 0:
				options[optionLine] = None
			else:
				options[optionLine[0:pos]] = optionLine[pos + 1:]

		# print("=>", (elements[0], elements[1], elements[2], options))

		return MountInfo(elements[0], elements[1], elements[2], options)
	#

#












