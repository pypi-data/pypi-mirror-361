









#
# This class represents various common mount options. <c>__str__()</c> is invoked by <c>Mounter.mount(...)</c> during a mount attempt in order to derive valid
# mount options from an instance of this class.
#
class MountOptions(object):

	################################################################################################################################
	## Constructor Methods
	################################################################################################################################

	def __init__(self):
		self._async = True
		self._atime = True
		self._diratime = True
		self._rw = True
		self._dev = True
		self._suid = True
		self._exec = True
		self._relatime = True
		self._dirsync = False
		self._uid = None
		self._gid = None
		self._remount = False

		"""
		# cifs
		self._user = None
		self._password = None
		self._credentials = None
		self._forceuid = False
		self._forcegid = False
		self._port = None
		self._netbiosname = None
		self._file_mode = None
		self._dir_mode = None
		self._domain = None
		"""
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	#
	# Attempt to remount an already-mounted filesystem. This is commonly used to change the mount flags for a filesystem, especially to make a readonly filesystem writeable. It does not change device or mount point.
	#
	@property
	def o_remount(self):
		return self._remount
	#

	@o_remount.setter
	def o_remount(self, value):
		assert isinstance(value, bool)
		self._remount = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Allow set-user-identifier or set-group-identifier bits to take effect.
	#
	@property
	def o_suid(self):
		return self._suid
	#

	@o_suid.setter
	def o_suid(self, value):
		assert isinstance(value, bool)
		self._suid = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Do not allow set-user-identifier or set-group-identifier bits to take effect. (This seems safe, but is in fact rather unsafe if you have suidperl(1) installed.)
	#
	@property
	def o_nosuid(self):
		return not self._suid
	#

	@o_nosuid.setter
	def o_nosuid(self, value):
		assert isinstance(value, bool)
		self._suid = not value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Update inode access times relative to modify or change time. Access time is only updated if the previous access time was earlier than the current modify or change time. (Similar to noatime, but doesn't break mutt or other applications that need to know if a file has been read since the last time it was modified.)
	#
	@property
	def o_relatime(self):
		return self._relatime
	#

	@o_relatime.setter
	def o_relatime(self, value):
		assert isinstance(value, bool)
		self._relatime = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Do not use relatime feature. See also the strictatime mount option.
	#
	@property
	def o_norelatime(self):
		return not self._relatime
	#

	@o_norelatime.setter
	def o_norelatime(self, value):
		assert isinstance(value, bool)
		self._relatime = not value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# All I/O to the filesystem should be done asynchronously. (See also the sync option.)
	#
	@property
	def o_async(self):
		return self._async
	#

	@o_async.setter
	def o_async(self, value):
		assert isinstance(value, bool)
		self._async = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# All I/O to the filesystem should be done synchronously. In case of media with limited number of write cycles (e.g. some flash drives) "sync" may cause life-cycle shortening.
	#
	@property
	def o_sync(self):
		return not self._async
	#

	@o_sync.setter
	def o_sync(self, value):
		assert isinstance(value, bool)
		self._async = not value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Do not update inode access times on this filesystem (e.g, for faster access on the news spool to speed up news servers).
	#
	@property
	def o_noatime(self):
		return not self._atime
	#

	@o_noatime.setter
	def o_noatime(self, value):
		assert isinstance(value, bool)
		self._atime = not value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Do not use noatime feature, then the inode access time is controlled by kernel defaults. See also the description for strictatime and relatime mount options.
	#
	@property
	def o_atime(self):
		return self._atime
	#

	@o_atime.setter
	def o_atime(self, value):
		assert isinstance(value, bool)
		self._atime = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Do not interpret character or block special devices on the file system.
	#
	@property
	def o_nodev(self):
		return not self._dev
	#

	@o_nodev.setter
	def o_nodev(self, value):
		assert isinstance(value, bool)
		self._dev = not value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Interpret character or block special devices on the filesystem.
	#
	@property
	def o_dev(self):
		return self._dev
	#

	@o_dev.setter
	def o_dev(self, value):
		assert isinstance(value, bool)
		self._dev = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Update directory inode access times on this filesystem. This is the default.
	#
	@property
	def o_diratime(self):
		return self._rw
	#

	@o_diratime.setter
	def o_diratime(self, value):
		assert isinstance(value, bool)
		self._diratime = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Do not update directory inode access times on this filesystem.
	#
	@property
	def o_nodiratime(self):
		return not self._diratime
	#

	@o_nodiratime.setter
	def o_nodiratime(self, value):
		assert isinstance(value, bool)
		self._diratime = not value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# All directory updates within the filesystem should be done synchronously. This affects the following system calls: creat, link, unlink, symlink, mkdir, rmdir, mknod and rename.
	#
	@property
	def o_dirsync(self):
		return self._dirsync
	#

	@o_dirsync.setter
	def o_dirsync(self, value):
		assert isinstance(value, bool)
		self._dirsync = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Permit execution of binaries.
	#
	@property
	def o_exec(self):
		return self._exec
	#

	@o_exec.setter
	def o_exec(self, value):
		assert isinstance(value, bool)
		self._exec = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Do not allow direct execution of any binaries on the mounted filesystem. (Until recently it was possible to run binaries anyway using a command like /lib/ld*.so /mnt/binary. This trick fails since Linux 2.4.25 / 2.6.0.)
	#
	@property
	def o_noexec(self):
		return not self._exec
	#

	@o_noexec.setter
	def o_noexec(self, value):
		assert isinstance(value, bool)
		self._exec = not value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Mount the filesystem read-write.
	#
	@property
	def o_rw(self):
		return self._rw
	#

	@o_rw.setter
	def o_rw(self, value):
		assert isinstance(value, bool)
		self._rw = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Set the owner of all files. (Default: the uid and gid of the current process.)
	#
	@property
	def o_uid(self):
		return self._uid
	#

	@o_uid.setter
	def o_uid(self, value):
		assert isinstance(value, (type(None), int, str))
		self._uid = value
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	#
	# Set the group of all files. (Default: the uid and gid of the current process.)
	#
	@property
	def o_gid(self):
		return self._gid

	@o_gid.setter
	def o_gid(self, value):
		assert isinstance(value, (type(None), int, str))
		self._gid = value

	# ----------------

	"""
	def user(self):
		return self._user

	@user.setter
	def user(self, value):
		assert isinstance(value, (type(None), str))
		self._user = value

	def password(self):
		return self._password

	@password.setter
	def password(self, value):
		assert isinstance(value, (type(None), str))
		self._password = value

	def credentials(self):
		return self._credentials

	@credentials.setter
	def credentials(self, value):
		assert isinstance(value, (type(None), str))
		self._credentials = value

	def forceuid(self):
		return self._forceuid

	@forceuid.setter
	def forceuid(self, value):
		assert isinstance(value, (type(None), str, int))
		self._forceuid = value

	def forcegid(self):
		return self._forcegid

	@forcegid.setter
	def forcegid(self, value):
		assert isinstance(value, (type(None), str, int))
		self._forcegid = value

	def port(self):
		return self._port

	@port.setter
	def port(self, value):
		assert isinstance(value, (type(None), int))
		self._port = value

	def netbiosname(self):
		return self._netbiosname

	@netbiosname.setter
	def netbiosname(self, value):
		assert isinstance(value, (type(None), str))
		self._netbiosname = value

	def file_mode(self):
		return self._file_mode

	@file_mode.setter
	def file_mode(self, value):
		assert isinstance(value, (type(None), int))
		self._file_mode = value

	def dir_mode(self):
		return self._dir_mode

	@dir_mode.setter
	def dir_mode(self, value):
		assert isinstance(value, (type(None), int))
		self._dir_mode = value

	def domain(self):
		return self._domain

	@domain.setter
	def domain(self, value):
		assert isinstance(value, (type(None), str))
		self._domain = value
	"""

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __repr__(self):
		return "MountOptions(" + self.__str__() + ")"
	#

	def __str__(self):
		s = ""

		if self._uid is not None:
			s += ",uid=" + str(self._uid)
		if self._gid is not None:
			s += ",gid=" + str(self._gid)
		if self._remount:
			s += ",remount"
		if not self._async:
			s += ",sync"
		if not self._atime:
			s += ",noatime"
		if not self._diratime:
			s += ",nodiratime"
		if not self._rw:
			s += ",ro"
		if not self._dev:
			s += ",nondev"
		if not self._suid:
			s += ",nosuid"
		if not self._exec:
			s += ",noexec"
		if not self._relatime:
			s += ",norelatime"
		if self._dirsync:
			s += ",dirsync"

		if len(s) > 0:
			return s[1:]
		else:
			return ""
	#

#




























