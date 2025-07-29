class PlatformNotSupportedError(Exception):
	"""
	Custom exception raised when the current platform is not supported.

	This exception is intended to be raised when the script or application is run on a platform that is not explicitly supported by the program logic.
	"""
	
	def __init__(self, platform: str):
		"""
		Initializes a new instance of `PlatformNotSupportedError`.

		Args:
		   platform (str): The name of the unsupported operating system.
		"""
		
		super().__init__(f"Platform not supported: {platform}.")
