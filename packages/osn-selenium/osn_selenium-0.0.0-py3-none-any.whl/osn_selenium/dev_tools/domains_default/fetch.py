import trio
from osn_selenium.dev_tools.utils import (
	TargetData,
	log_exception
)
from typing import (
	Any,
	Literal,
	Sequence,
	TYPE_CHECKING,
	TypedDict,
	Union
)


if TYPE_CHECKING:
	from osn_selenium.dev_tools.manager import DevToolsTarget
	from osn_selenium.dev_tools.domains.fetch import request_paused_actions_literal, auth_required_actions_literal


def request_paused_choose_func(self: "DevToolsTarget", event: Any) -> Sequence["request_paused_actions_literal"]:
	"""
	Default function to choose actions for a 'fetch.RequestPaused' event.

	This default implementation always chooses to 'continue_request'.
	Users can provide their own function to implement custom logic for
	deciding which actions to take based on the event details.

	Args:
		self (DevToolsTarget): The DevToolsTarget instance.
		event (Any): The 'RequestPaused' event object.

	Returns:
		Sequence[request_paused_actions_literal]: A sequence of action names to be executed.
	"""
	
	return ["continue_request"]


def on_error_func(self: "DevToolsTarget", event: Any, error: BaseException):
	"""
	Default error handling function for DevTools event listeners.

	This function simply logs the error using the internal error logging utility.
	Users can provide their own function to implement custom error handling logic.

	Args:
		self (DevToolsTarget): The DevToolsTarget instance.
		event (Any): The event object that was being processed when the error occurred.
		error (BaseException): The exception that was raised.
	"""
	
	log_exception(error)


class HeaderInstance(TypedDict):
	"""
	Type definition for header modification instructions used by the `headers_handler`.

	This TypedDict is used to specify how a header should be modified when intercepting network requests using DevTools.
	It includes the new value for the header and an instruction on how to apply the change (set, set if exists, remove).

	Attributes:
		value (Union[str, Any]): The new value to set for the header. Can be a string or any other type that can be converted to a string for the header value.
		instruction (Literal["set", "set_exist", "remove"]): Specifies the type of modification to apply to the header.

			- "set": Sets the header to the provided `value`, overwriting any existing value or adding it if not present.
			- "set_exist": Sets the header to the provided `value` only if the header already exists in the request.
			- "remove": Removes the header from the request if it exists.
	"""
	
	value: Union[str, Any]
	instruction: Union[Literal["set", "set_exist", "remove"], Any]


async def headers_handler(
		self: "DevToolsTarget",
		ready_event: trio.Event,
		headers_instances: dict[str, HeaderInstance],
		event: Any,
		kwargs: dict[str, Any]
):
	"""
	A parameter handler function to modify request headers.

	This handler processes a dictionary of header modification instructions (`headers_instances`)
	and applies them to the request headers found in the `event` object. The modified headers
	are then added to the `kwargs` dictionary, which will be used for a CDP command
	like `fetch.continueRequest`.

	Args:
		self (DevToolsTarget): The DevToolsTarget instance.
		ready_event (trio.Event): A Trio event to signal when the handler has completed its work.
		headers_instances (dict[str, HeaderInstance]): A dictionary where keys are header names
			and values are `HeaderInstance` objects defining the modification.
		event (Any): The CDP event object (e.g., `RequestPaused`) containing the original request headers.
		kwargs (dict[str, Any]): The dictionary of keyword arguments to which the modified headers will be added.

	Raises:
		Exception: If an error occurs during header modification.
	"""
	
	try:
		header_entry_class = await self.get_devtools_object("fetch.HeaderEntry")
		headers = {name: value for name, value in event.request.headers.items()}
	
		for name, instance in headers_instances.items():
			value = instance["value"]
			instruction = instance["instruction"]
	
			if instruction == "set":
				headers[name] = value
				continue
	
			if instruction == "set_exist":
				if name in headers:
					headers[name] = value
	
				continue
	
			if instruction == "remove":
				if name in headers:
					headers.pop(name)
	
				continue
	
		kwargs["headers"] = [
			header_entry_class(name=name, value=value)
			for name, value in headers.items()
		]
	
		ready_event.set()
	except BaseException as error:
		await self.log_error(error=error)
		raise error


def auth_required_choose_func(self: "DevToolsTarget", target_data: TargetData, event: Any) -> Sequence["auth_required_actions_literal"]:
	"""
	Default function to choose actions for a 'fetch.AuthRequired' event.

	This default implementation always chooses to 'continue_with_auth'.
	Users can provide their own function to implement custom logic for
	deciding which actions to take based on the event details.

	Args:
		self (DevToolsTarget): The DevToolsTarget instance.
		target_data (TargetData): Data about the current browser target.
		event (Any): The 'AuthRequired' event object.

	Returns:
		Sequence[auth_required_actions_literal]: A sequence of action names to be executed.
	"""
	
	return ["continue_with_auth"]
