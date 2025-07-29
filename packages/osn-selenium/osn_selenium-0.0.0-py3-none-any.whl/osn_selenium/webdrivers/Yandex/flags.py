import pathlib
from typing import (
	Optional,
	TypedDict,
	Union
)
from selenium.webdriver.chrome.options import Options
from osn_selenium.webdrivers.Blink.flags import BlinkFeatures
from osn_selenium.webdrivers.types import (
	FlagDefinition,
	FlagType
)
from osn_selenium.webdrivers.Chrome.flags import (
	ChromeArguments,
	ChromeAttributes,
	ChromeExperimentalOptions,
	ChromeFlagsManager
)


class YandexFlagsManager(ChromeFlagsManager):
	"""
	Manages Yandex Browser-specific options for Selenium WebDriver.

	This class extends BrowserOptionsManager to provide specific configurations
	for Yandex Browser options, such as experimental options and arguments.

	Attributes:
	"""
	
	def __init__(
			self,
			browser_exe: Optional[Union[str, pathlib.Path]] = None,
			start_page_url: Optional[str] = None,
			flags_types: Optional[dict[str, FlagType]] = None,
			flags_definitions: Optional[dict[str, FlagDefinition]] = None
	):
		"""
		Initializes YandexOptionsManager.

		Sets up the Yandex Browser options manager with specific option configurations for
		debugging port, user agent, proxy, and BiDi protocol.
		"""
		
		yandex_flags_types = {}
		
		if flags_types is not None:
			yandex_flags_types.update(flags_types)
		
		yandex_flags_definitions = {}
		
		if flags_definitions is not None:
			yandex_flags_definitions.update(flags_definitions)
		
		super().__init__(
				browser_exe=browser_exe,
				start_page_url=start_page_url,
				flags_types=yandex_flags_types,
				flags_definitions=yandex_flags_definitions,
		)
	
	def _renew_webdriver_options(self) -> Options:
		"""
		Creates and returns a new Options object.

		Returns a fresh instance of `webdriver.ChromeOptions`, as Yandex Browser is based on Chromium,
		allowing for a clean state of browser options to be configured.

		Returns:
			Options: A new Selenium Yandex Browser options object, based on ChromeOptions.
		"""
		
		return Options()


class YandexAttributes(ChromeAttributes, total=False):
	"""
	Typed dictionary for WebDriver attributes specific to Yandex browsers.

	Attributes:
		enable_bidi (Optional[bool]): Enables/disables BiDi (Bidirectional) protocol mapper.
	"""
	
	pass


class YandexExperimentalOptions(ChromeExperimentalOptions, total=False):
	"""
	Typed dictionary for experimental options specific to Yandex browsers.

	Attributes:
		debugger_address (Optional[str]): The address (IP:port) of the remote debugger.
	"""
	
	pass


class YandexArguments(ChromeArguments, total=False):
	"""
	Typed dictionary for command-line arguments specific to Yandex browsers.

	Attributes:
		se_downloads_enabled (bool): Enables/disables Selenium downloads.
		headless_mode (bool): Runs the browser in headless mode (without a UI).
		mute_audio (bool): Mutes audio output from the browser.
		no_first_run (bool): Prevents the browser from showing the "first run" experience.
		disable_background_timer_throttling (bool): Disables throttling of background timers.
		disable_backgrounding_occluded_windows (bool): Prevents backgrounding of occluded windows.
		disable_hang_monitor (bool): Disables the browser's hang monitor.
		disable_ipc_flooding_protection (bool): Disables IPC flooding protection.
		disable_renderer_backgrounding (bool): Prevents renderer processes from being backgrounded.
		disable_back_forward_cache (bool): Disables the Back-Forward Cache.
		disable_notifications (bool): Disables web notifications.
		disable_popup_blocking (bool): Disables the built-in popup blocker.
		disable_prompt_on_repost (bool): Disables the prompt when reposting form data.
		disable_sync (bool): Disables browser synchronization features.
		disable_background_networking (bool): Disables background network activity.
		disable_breakpad (bool): Disables the crash reporter.
		disable_component_update (bool): Disables component updates.
		disable_domain_reliability (bool): Disables domain reliability monitoring.
		disable_new_content_rendering_timeout (bool): Disables timeout for new content rendering.
		disable_threaded_animation (bool): Disables threaded animation.
		disable_threaded_scrolling (bool): Disables threaded scrolling.
		disable_checker_imaging (bool): Disables checker imaging.
		disable_image_animation_resync (bool): Disables image animation resynchronization.
		disable_partial_raster (bool): Disables partial rasterization.
		disable_skia_runtime_opts (bool): Disables Skia runtime optimizations.
		disable_dev_shm_usage (bool): Disables the use of /dev/shm (important for Docker).
		disable_gpu (bool): Disables GPU hardware acceleration.
		aggressive_cache_discard (bool): Enables aggressive discarding of cached data.
		allow_running_insecure_content (bool): Allows running insecure content on HTTPS pages.
		no_process_per_site (bool): Runs all sites in a single process (less secure, but saves memory).
		enable_precise_memory_info (bool): Enables precise memory information reporting.
		use_fake_device_for_media_stream (bool): Uses a fake camera/microphone for media streams.
		use_fake_ui_for_media_stream (bool): Uses a fake UI for media stream requests.
		deny_permission_prompts (bool): Automatically denies all permission prompts.
		disable_external_intent_requests (bool): Disables external intent requests.
		noerrdialogs (bool): Suppresses error dialogs.
		enable_automation (bool): Enables automation features.
		test_type (bool): Sets the browser to test mode.
		remote_debugging_pipe (bool): Uses a pipe for remote debugging instead of a port.
		silent_debugger_extension_api (bool): Silences debugger extension API warnings.
		enable_logging_stderr (bool): Enables logging to stderr.
		password_store_basic (bool): Uses a basic password store.
		use_mock_keychain (bool): Uses a mock keychain for testing.
		enable_crash_reporter_for_testing (bool): Enables crash reporter for testing purposes.
		metrics_recording_only (bool): Records metrics without sending them.
		no_pings (bool): Disables sending pings.
		allow_pre_commit_input (bool): Allows pre-commit input.
		deterministic_mode (bool): Runs the browser in a more deterministic mode.
		run_all_compositor_stages_before_draw (bool): Runs all compositor stages before drawing.
		enable_begin_frame_control (bool): Enables begin frame control.
		in_process_gpu (bool): Runs the GPU process in-process.
		block_new_web_contents (bool): Blocks new web contents (e.g., pop-ups).
		new_window (bool): Opens a new window instead of a new tab.
		no_service_autorun (bool): Disables service autorun.
		process_per_tab (bool): Runs each tab in its own process.
		single_process (bool): Runs the browser in a single process (less stable).
		no_sandbox (bool): Disables the sandbox (less secure, but can fix some issues).
		user_agent (Optional[str]): Sets a custom user agent string.
		user_data_dir (Optional[str]): Specifies the user data directory.
		proxy_server (Optional[str]): Specifies a proxy server to use.
		remote_debugging_port (Optional[int]): Specifies the remote debugging port.
		remote_debugging_address (Optional[str]): Specifies the remote debugging address.
		use_file_for_fake_video_capture (Optional[Union[str, pathlib.Path]]): Uses a file for fake video capture.
		autoplay_policy (Optional[AutoplayPolicyType]): Sets the autoplay policy.
		log_level (Optional[LogLevelType]): Sets the browser's log level.
		use_gl (Optional[UseGLType]): Specifies the GL backend to use.
		force_color_profile (Optional[str]): Forces a specific color profile.
	"""
	
	pass


class YandexFlags(TypedDict, total=False):
	"""
	Typed dictionary representing a collection of all flag types for Yandex browsers.

	This combines arguments, experimental options, attributes, and Blink features
	that are specific to Yandex browsers.

	Attributes:
		argument (YandexArguments): Command-line arguments for the Yandex browser.
		experimental_option (YandexExperimentalOptions): Experimental options for WebDriver specific to Yandex.
		attribute (YandexAttributes): WebDriver attributes specific to Yandex.
		blink_feature (BlinkFeatures): Blink-specific feature flags.
	"""
	
	argument: YandexArguments
	experimental_option: YandexExperimentalOptions
	attribute: YandexAttributes
	blink_feature: BlinkFeatures
