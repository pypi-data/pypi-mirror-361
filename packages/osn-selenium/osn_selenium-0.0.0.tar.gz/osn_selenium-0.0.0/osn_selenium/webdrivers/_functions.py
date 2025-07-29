import re
import sys
import math
import pathlib
from copy import deepcopy
from random import randint
from subprocess import PIPE, Popen
from typing import Optional, Union
from pandas import DataFrame, Series
from osn_selenium.errors import (
	PlatformNotSupportedError
)
from osn_windows_cmd.netstat import (
	get_netstat_connections_data as windows_netstat_connections_data
)
from osn_selenium.webdrivers.types import (
	ActionPoint,
	JS_Scripts,
	MoveOffset,
	MovePart,
	ScrollDelta,
	ScrollPart,
	TextInputPart,
	_MoveStep
)


def text_input_to_parts(text: str) -> list[TextInputPart]:
	"""
	Breaks down a text string into smaller parts for simulating human-like typing.

	Generates a list of `TextInputPart` objects, where each part contains a character
	or sequence of characters and a calculated duration. The duration simulates pauses
	between key presses, with potentially longer pauses between different consecutive
	characters.

	Args:
		text (str): The input string to be broken down.

	Returns:
		list[TextInputPart]: A list of `TextInputPart` objects representing the sequence
							 of text segments and their associated durations for simulated typing.
	"""
	
	parts = []
	previous_sign = None
	
	for sign in text:
		if previous_sign is None or sign == previous_sign:
			parts.append(TextInputPart(text=sign, duration=randint(50, 70)))
		else:
			parts.append(TextInputPart(text=sign, duration=randint(100, 200)))
	
		previous_sign = sign
	
	return parts


def str_adding_validation_function(value: Optional[str]) -> bool:
	"""
	Validation function that checks if a value is a non-empty string.

	Args:
		value (Optional[str]): The value to validate.

	Returns:
		bool: `True` if the value is a non-empty string, `False` otherwise.
	"""
	
	if value is not None and not isinstance(value, str):
		return False
	
	return bool(value)


def scroll_to_parts(start_position: ActionPoint, end_position: ActionPoint) -> list[ScrollPart]:
	"""
	Calculates a sequence of smaller scroll steps with durations for human-like scrolling.

	Simulates scrolling by generating a series of vertical steps followed by horizontal steps
	until the target coordinates are reached. Each step is represented by a `ScrollPart`
	containing the scroll delta for that step and a random duration.

	Args:
		start_position (ActionPoint): The starting conceptual scroll position.
		end_position (ActionPoint): The target conceptual scroll position.

	Returns:
		list[ScrollPart]: A list of `ScrollPart` objects representing the sequence of scroll
						  movements and their associated durations. The `delta` in each part
						  represents the scroll amount for that step, and the `point` represents
						  the conceptual position *after* applying that delta.
	"""
	
	parts = []
	
	current_position = deepcopy(start_position)
	
	if start_position.y != end_position.y:
		while current_position.y != end_position.y:
			offset = randint(5, 20)
	
			if start_position.y > end_position.y:
				offset *= -1
	
			if start_position.y < end_position.y:
				if current_position.y + offset > end_position.y:
					offset = end_position.y - current_position.y
			elif start_position.y > end_position.y:
				if current_position.y + offset < end_position.y:
					offset = end_position.y - current_position.y
	
			current_position.y += offset
			parts.append(
					ScrollPart(
							point=deepcopy(current_position),
							delta=ScrollDelta(x=0, y=offset),
							duration=randint(1, 4)
					)
			)
	
	if start_position.x != end_position.x:
		while current_position.x != end_position.x:
			offset = randint(5, 20)
	
			if start_position.x > end_position.x:
				offset *= -1
	
			if start_position.x <= end_position.x:
				if current_position.x + offset > end_position.x:
					offset = end_position.x - current_position.x
			elif start_position.x > end_position.x:
				if current_position.x + offset < end_position.x:
					offset = current_position.x - end_position.x
	
			current_position.x += offset
			parts.append(
					ScrollPart(
							point=deepcopy(current_position),
							delta=ScrollDelta(x=offset, y=0),
							duration=randint(1, 4)
					)
			)
	
	return parts


def read_js_scripts() -> JS_Scripts:
	"""
	Reads JavaScript scripts from files and returns them in a _JS_Scripts object.

	This function locates all `.js` files within the 'js_scripts' directory, which is expected to be located two levels above the current file's directory.
	It reads the content of each JavaScript file, using UTF-8 encoding, and stores these scripts in a dictionary-like `_JS_Scripts` object.
	The filenames (without the `.js` extension) are used as keys in the `_JS_Scripts` object to access the script content.

	Returns:
		JS_Scripts: An object of type _JS_Scripts, containing the content of each JavaScript file as attributes.
	"""
	
	scripts = {}
	
	for script_file in (pathlib.Path(__file__).parent / "js_scripts").iterdir():
		scripts[re.sub(r"\.js$", "", script_file.name)] = open(script_file, "r", encoding="utf-8").read()
	
	return JS_Scripts(
			check_element_in_viewport=scripts["check_element_in_viewport"],
			get_document_scroll_size=scripts["get_document_scroll_size"],
			get_element_css=scripts["get_element_css"],
			get_element_rect_in_viewport=scripts["get_element_rect_in_viewport"],
			get_random_element_point_in_viewport=scripts["get_random_element_point_in_viewport"],
			get_viewport_position=scripts["get_viewport_position"],
			get_viewport_rect=scripts["get_viewport_rect"],
			get_viewport_size=scripts["get_viewport_size"],
			open_new_tab=scripts["open_new_tab"],
			stop_window_loading=scripts["stop_window_loading"],
	)


def path_adding_validation_function(value: Optional[Union[str, pathlib.Path]]) -> bool:
	"""
	Validation function that checks if a value is a non-empty string or a pathlib.Path object.

	Args:
		value (Optional[Union[str, pathlib.Path]]): The value to validate.

	Returns:
		bool: `True` if the value is a valid path-like object, `False` otherwise.
	"""
	
	if value is not None and not isinstance(value, (str, pathlib.Path)):
		return False
	
	return bool(value)


def optional_bool_adding_validation_function(value: Optional[bool]) -> bool:
	"""
	Validation function that checks if a value is a boolean or None.

	The function returns `True` if the value is not None, allowing the flag
	to be added.

	Args:
		value (Optional[bool]): The value to validate.

	Returns:
		bool: `True` if the value is not None, `False` if the value is not a boolean.
	"""
	
	if value is not None and not isinstance(value, bool):
		return False
	
	return value is not None


def move_to_parts(start_position: ActionPoint, end_position: ActionPoint) -> list[MovePart]:
	"""
	Calculates a sequence of smaller move steps with durations for human-like mouse movement.

	Generates a path between a start and end point that deviates slightly from a
	straight line using a sinusoidal function, simulating more natural mouse movement.
	The path is broken into segments, each represented by a `MovePart` object specifying
	the target point for that segment, the offset from the previous point, and a random duration.

	Args:
		start_position (ActionPoint): The starting coordinates for the movement.
		end_position (ActionPoint): The target coordinates for the movement.

	Returns:
		list[MovePart]: A list of `MovePart` objects representing the sequence of mouse
						movements and their associated durations. Each `MovePart` indicates
						the `point` to move to, the `offset` from the previous point,
						and the `duration` for that movement segment.
	"""
	
	def get_new_position():
		"""Calculates random horizontal and vertical amplitudes for deviation."""
		
		linear_progress = step.index / len(steps)
		
		deviation_x = step.amplitude_x * math.sin(linear_progress * 2 * math.pi)
		current_x_linear = start_position.x + (end_position.x - start_position.x) * linear_progress
		
		deviation_y = step.amplitude_y * math.cos(linear_progress * 2 * math.pi)
		current_y_linear = start_position.y + (end_position.y - start_position.y) * linear_progress
		
		return ActionPoint(
				x=int(current_x_linear + deviation_x),
				y=int(current_y_linear + deviation_y)
		)
	
	def get_amplitude():
		"""Generates a sequence of internal _MoveStep objects."""
		
		amplitude_x = randint(10, 20)
		amplitude_y = randint(10, 20)
		
		if start_position.x > end_position.x:
			amplitude_x *= -1
		
		if start_position.y > end_position.y:
			amplitude_y *= -1
		
		return amplitude_x, amplitude_y
	
	def calculate_steps():
		"""Calculates the target point for a move step, including sinusoidal deviation."""
		
		steps_ = []
		current_point = deepcopy(start_position)
		index = 0
		
		while current_point != end_position:
			amplitude_x, amplitude_y = get_amplitude()
			steps_.append(_MoveStep(amplitude_x=amplitude_x, amplitude_y=amplitude_y, index=index))
		
			index += 1
		
			if start_position.x <= end_position.x:
				current_point.x += amplitude_x if current_point.x + amplitude_x <= end_position.x else end_position.x - current_point.x
			else:
				current_point.x += amplitude_x if current_point.x + amplitude_x >= end_position.x else end_position.x - current_point.x
		
			if start_position.y <= end_position.y:
				current_point.y += amplitude_y if current_point.y + amplitude_y <= end_position.y else end_position.y - current_point.y
			else:
				current_point.y += amplitude_y if current_point.y + amplitude_y >= end_position.y else end_position.y - current_point.y
		
		return steps_
	
	parts = []
	steps = calculate_steps()
	previous_position = deepcopy(start_position)
	
	for step in steps:
		new_position = get_new_position()
	
		if start_position.x <= end_position.x:
			new_position.x = int(new_position.x if new_position.x < end_position.x else end_position.x)
		else:
			new_position.x = int(new_position.x if new_position.x > end_position.x else end_position.x)
	
		if start_position.y <= end_position.y:
			new_position.y = int(new_position.y if new_position.y < end_position.y else end_position.y)
		else:
			new_position.y = int(new_position.y if new_position.y > end_position.y else end_position.y)
	
		parts.append(
				MovePart(
						point=new_position,
						offset=MoveOffset(
								x=new_position.x - previous_position.x,
								y=new_position.y - previous_position.y
						),
						duration=randint(1, 4)
				)
		)
	
		previous_position = deepcopy(new_position)
	
		if parts[-1].point == end_position:
			break
	
	if parts[-1].point != end_position:
		parts.append(
				MovePart(
						point=end_position,
						offset=MoveOffset(
								x=end_position.x - previous_position.x,
								y=end_position.y - previous_position.y
						),
						duration=randint(1, 4)
				)
		)
	
	return parts


def int_adding_validation_function(value: Optional[int]) -> bool:
	"""
	Validation function that checks if a value is an integer.

	Args:
		value (Optional[int]): The value to validate.

	Returns:
		bool: `True` if the value is an integer or None, `False` otherwise.
	"""
	
	if value is not None and not isinstance(value, int):
		return False
	
	return True


def get_found_profile_dir(data: Series, profile_dir_command: str) -> Optional[str]:
	"""
	Extracts the browser profile directory path from a process's command line arguments.

	This function executes a platform-specific command to retrieve the command line
	of a process given its PID. It then searches for a profile directory path within
	the command line using a provided command pattern. Currently, only Windows platform is supported.

	Args:
		data (Series): A Pandas Series containing process information, which must include a 'PID' column
			representing the process ID.
		profile_dir_command (str): A string representing the command line pattern to search for the profile directory.
			This string should contain '{value}' as a placeholder where the profile directory path is expected.
			For example: "--user-data-dir='{value}'".

	Returns:
		Optional[str]: The profile directory path as a string if found in the command line, otherwise None.

	Raises:
		PlatformNotSupportedError: If the platform is not supported.
	"""
	
	if sys.platform == "win32":
		stdout = Popen(
				f"wmic process where processid={int(data['PID'])} get CommandLine /FORMAT:LIST",
				stdout=PIPE,
				shell=True
		).communicate()[0].decode("866", errors="ignore").strip()
		found_command_line = re.sub(r"^CommandLine=", "", stdout).strip()
	
		found_profile_dir = re.search(profile_dir_command.format(value="(.*?)"), found_command_line)
		if found_profile_dir is not None:
			found_profile_dir = found_profile_dir.group(1)
	
		return found_profile_dir
	
	raise PlatformNotSupportedError(f"Unsupported platform: {sys.platform}.")


def get_active_executables_table(browser_exe: Union[str, pathlib.Path]) -> DataFrame:
	"""
	Retrieves a table of active executables related to a specified browser, listening on localhost.

	This function uses platform-specific methods to fetch network connection information
	and filters it to find entries associated with the provided browser executable
	that are in a "LISTENING" state on localhost. Currently, only Windows platform is supported.

	Args:
		browser_exe (Union[str, pathlib.Path]): The path to the browser executable.
			It can be a string or a pathlib.Path object.

	Returns:
		DataFrame: A Pandas DataFrame containing rows of active executable connections
			that match the browser executable and listening criteria.
			Returns an empty DataFrame if no matching executables are found.

	Raises:
		PlatformNotSupportedError: If the platform is not supported.
	"""
	
	if sys.platform == "win32":
		connections_data = windows_netstat_connections_data(
				show_all_ports=True,
				show_connections_exe=True,
				show_connection_pid=True
		)
	
		return connections_data.loc[
			(
					connections_data["Executable"] == (browser_exe if isinstance(browser_exe, str) else browser_exe.name)
			) &
			connections_data["Local Address"].str.contains(r"127\.0\.0\.1:\d+", regex=True, na=False) &
			(connections_data["State"] == "LISTENING")
		]
	
	raise PlatformNotSupportedError(f"Unsupported platform: {sys.platform}.")


def find_browser_previous_session(
		browser_exe: Union[str, pathlib.Path],
		profile_dir_command: str,
		profile_dir: Optional[str]
) -> Optional[int]:
	"""
	Finds the port number of a previously opened browser session, if it exists.

	This function checks for an existing browser session by examining network connections.
	It searches for listening connections associated with the given browser executable and profile directory.

	Args:
		browser_exe (Union[str, pathlib.Path]): Path to the browser executable or just the executable name.
		profile_dir_command (str): Command line pattern to find the profile directory argument in the process command line. Should use `{value}` as a placeholder for the directory path.
		profile_dir (Optional[str]): The expected profile directory path to match against.

	Returns:
		Optional[int]: The port number of the previous session if found and matched, otherwise None.
	"""
	
	executables_table = get_active_executables_table(browser_exe)
	
	for index, row in executables_table.iterrows():
		found_profile_dir = get_found_profile_dir(row, profile_dir_command)
	
		if found_profile_dir == profile_dir:
			return int(re.search(r"127\.0\.0\.1:(\d+)", row["Local Address"]).group(1))
	
	return None


def build_first_start_argument(browser_exe: Union[str, pathlib.Path]) -> str:
	"""
	Builds the first command line argument to start a browser executable.

	This function constructs the initial command line argument needed to execute a browser,
	handling different operating systems and executable path formats.

	Args:
		browser_exe (Union[str, pathlib.Path]): Path to the browser executable or just the executable name.

	Returns:
		str: The constructed command line argument string.

	Raises:
		TypeError: If `browser_exe` is not of type str or pathlib.Path.
	"""
	
	if isinstance(browser_exe, str):
		return browser_exe
	elif isinstance(browser_exe, pathlib.Path):
		return f"\"{str(browser_exe.resolve())}\""
	else:
		raise TypeError(f"browser_exe must be str or pathlib.Path, not {type(browser_exe)}.")


def bool_adding_validation_function(value: Optional[bool]) -> bool:
	"""
	Validation function that checks if a value is a boolean and `True`.

	Args:
		value (Optional[bool]): The value to validate.

	Returns:
		bool: `True` if the value is `True`, `False` otherwise.
	"""
	
	if not isinstance(value, bool):
		return False
	
	return value
