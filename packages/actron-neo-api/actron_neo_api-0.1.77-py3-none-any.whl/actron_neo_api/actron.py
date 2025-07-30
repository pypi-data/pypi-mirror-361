import logging
import asyncio
from typing import Dict, List, Optional, Union, Any

import aiohttp

from .oauth import OAuth2DeviceCodeAuth
from .commands import CommandBuilder
from .state import StateManager
from .exceptions import ActronNeoAPIError, ActronNeoAuthError
from .models import ActronAirNeoStatus

_LOGGER = logging.getLogger(__name__)

class ActronNeoAPI:
    """
    Client for the Actron Neo API with improved architecture.

    This client provides a modern, structured approach to interacting with
    the Actron Neo API while maintaining compatibility with the previous interface.
    """

    def __init__(
        self,
        base_url: str = "https://nimbus.actronair.com.au",
        oauth2_client_id: str = "home_assistant",
    ):
        """
        Initialize the ActronNeoAPI client with OAuth2 authentication.

        Args:
            base_url: Base URL for the Actron Neo API
            oauth2_client_id: OAuth2 client ID for device code flow
        """
        self.base_url = base_url

        # Initialize OAuth2 authentication
        self.oauth2_auth = OAuth2DeviceCodeAuth(base_url, oauth2_client_id)

        self.state_manager = StateManager()
        # Set the API reference in the state manager for command execution
        self.state_manager.set_api(self)

        self.systems = []

        # Session management
        self._session = None
        self._session_lock = asyncio.Lock()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp ClientSession."""
        async with self._session_lock:
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession()
            return self._session

    async def close(self) -> None:
        """Close the API client and release resources."""
        async with self._session_lock:
            if self._session and not self._session.closed:
                await self._session.close()
                self._session = None

    async def __aenter__(self):
        """Support for async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support for async context manager."""
        await self.close()

    # OAuth2 Device Code Flow methods

    async def request_device_code(self) -> Dict[str, Any]:
        """
        Request a device code for OAuth2 device code flow.
        
        Returns:
            Dictionary containing device code, user code, verification URI, etc.
            
        Raises:
            ActronNeoAuthError: If device code request fails
        """
        return await self.oauth2_auth.request_device_code()

    async def poll_for_token(self, device_code: str) -> Optional[Dict[str, Any]]:
        """
        Poll for access token using device code.
        
        Args:
            device_code: The device code received from request_device_code
            
        Returns:
            Token data if successful, None if still pending
            
        Raises:
            ActronNeoAuthError: If polling fails
        """
        return await self.oauth2_auth.poll_for_token(device_code)

    async def get_user_info(self) -> Dict[str, Any]:
        """
        Get user information using the access token.
        
        Returns:
            Dictionary containing user information
            
        Raises:
            ActronNeoAuthError: If user info request fails
        """
        return await self.oauth2_auth.get_user_info()

    def set_oauth2_tokens(self, access_token: str, refresh_token: Optional[str] = None, 
                         expires_in: Optional[int] = None, token_type: str = "Bearer") -> None:
        """
        Set OAuth2 tokens manually (useful for restoring saved tokens).
        
        Args:
            access_token: The access token
            refresh_token: The refresh token (optional)
            expires_in: Token expiration time in seconds from now (optional)
            token_type: Token type (default: "Bearer")
        """
        self.oauth2_auth.set_tokens(access_token, refresh_token, expires_in, token_type)

    async def _handle_request(self, request_func, *args, **kwargs):
        """
        Handle API requests, retrying if the token is expired.
        """
        try:
            # Ensure the token is valid before making the request
            if self.oauth2_auth.is_token_expiring_soon:
                _LOGGER.info("Access token is about to expire. Proactively refreshing.")
                await self.oauth2_auth.refresh_access_token()

            return await request_func(*args, **kwargs)
        except ActronNeoAuthError as e:
            # Try to refresh the token and retry on auth errors
            if "invalid_token" in str(e).lower() or "token_expired" in str(e).lower():
                _LOGGER.warning("Access token expired or invalid. Attempting to refresh.")
                await self.oauth2_auth.refresh_access_token()
                return await request_func(*args, **kwargs)
            raise
        except aiohttp.ClientResponseError as e:
            if e.status == 401:  # HTTP 401 Unauthorized
                _LOGGER.warning("Access token expired (401 Unauthorized). Refreshing token.")
                await self.oauth2_auth.refresh_access_token()
                return await request_func(*args, **kwargs)
            raise

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an API request with proper error handling.

        Args:
            method: HTTP method ("get", "post", etc.)
            endpoint: API endpoint (without base URL)
            params: URL parameters
            json_data: JSON body data
            data: Form data
            headers: HTTP headers

        Returns:
            API response as JSON

        Raises:
            ActronNeoAuthError: For authentication errors
            ActronNeoAPIError: For API errors
        """
        # Ensure we have a valid token
        await self.oauth2_auth.ensure_token_valid()
        auth_header = self.oauth2_auth.authorization_header

        # Prepare the request
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = headers or {}
        request_headers.update(auth_header)

        # Get a session
        session = await self._get_session()

        # Make the request
        try:
            async with session.request(
                method,
                url,
                params=params,
                json=json_data,
                data=data,
                headers=request_headers
            ) as response:
                if response.status == 401:
                    response_text = await response.text()
                    raise ActronNeoAuthError(f"Authentication failed: {response_text}")

                if response.status != 200:
                    response_text = await response.text()
                    raise ActronNeoAPIError(
                        f"API request failed. Status: {response.status}, Response: {response_text}"
                    )

                return await response.json()
        except aiohttp.ClientError as e:
            raise ActronNeoAPIError(f"Request failed: {str(e)}")

    # API Methods

    async def get_ac_systems(self) -> List[Dict[str, Any]]:
        """
        Retrieve all AC systems in the customer account.

        Returns:
            List of AC systems
        """
        return await self._handle_request(self._get_ac_systems)

    async def _get_ac_systems(self) -> List[Dict[str, Any]]:
        """Internal method to perform the actual API call."""
        response = await self._make_request(
            "get",
            "api/v0/client/ac-systems",
            params={"includeNeo": "true"}
        )
        return response["_embedded"]["ac-system"]

    async def get_ac_status(self, serial_number: str) -> Dict[str, Any]:
        """
        Retrieve the full status of a specific AC system by serial number.

        Args:
            serial_number: Serial number of the AC system

        Returns:
            Full status of the AC system
        """
        return await self._handle_request(self._get_ac_status, serial_number)

    async def _get_ac_status(self, serial_number: str) -> Dict[str, Any]:
        """Internal method to perform the actual API call."""
        return await self._make_request(
            "get",
            "api/v0/client/ac-systems/status/latest",
            params={"serial": serial_number}
        )

    async def get_ac_events(
        self, serial_number: str, event_type: str = "latest", event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve events for a specific AC system.

        Args:
            serial_number: Serial number of the AC system
            event_type: 'latest', 'newer', or 'older' for the event query type
            event_id: The event ID for 'newer' or 'older' event queries

        Returns:
            Events of the AC system
        """
        return await self._handle_request(
            self._get_ac_events, serial_number, event_type, event_id
        )

    async def _get_ac_events(
        self, serial_number: str, event_type: str = "latest", event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Internal method to perform the actual API call."""
        params = {"serial": serial_number}

        if event_type == "latest":
            endpoint = "api/v0/client/ac-systems/events/latest"
        elif event_type == "newer" and event_id:
            endpoint = "api/v0/client/ac-systems/events/newer"
            params["newerThanEventId"] = event_id
        elif event_type == "older" and event_id:
            endpoint = "api/v0/client/ac-systems/events/older"
            params["olderThanEventId"] = event_id
        else:
            raise ValueError(
                "Invalid event_type or missing event_id for 'newer'/'older' event queries."
            )

        return await self._make_request("get", endpoint, params=params)

    async def get_user(self) -> Dict[str, Any]:
        """
        Get user data from the API.

        Returns:
            User account data
        """
        return await self._handle_request(self._get_user)

    async def _get_user(self) -> Dict[str, Any]:
        """Internal method to perform the actual API call."""
        return await self._make_request("get", "api/v0/client/account")

    async def send_command(self, serial_number: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a command to the specified AC system.

        Args:
            serial_number: Serial number of the AC system
            command: Dictionary containing the command details

        Returns:
            Command response
        """
        return await self._handle_request(self._send_command, serial_number, command)

    async def _send_command(self, serial_number: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to perform the actual API call."""
        serial_number = serial_number.lower()
        return await self._make_request(
            "post",
            "api/v0/client/ac-systems/cmds/send",
            params={"serial": serial_number},
            json_data=command,
            headers={"Content-Type": "application/json"}
        )

    # Convenience methods for common operations

    async def set_system_mode(self, serial_number: str, is_on: bool, mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Set the AC system mode.

        Args:
            serial_number: Serial number of the AC system
            is_on: Boolean to turn the system on or off
            mode: Mode to set when the system is on ('AUTO', 'COOL', 'FAN', 'HEAT')

        Returns:
            Command response
        """
        command = CommandBuilder.set_system_mode(is_on, mode)
        return await self.send_command(serial_number, command)

    async def set_fan_mode(
        self, serial_number: str, fan_mode: str, continuous: bool = False
    ) -> Dict[str, Any]:
        """
        Set the fan mode of the AC system.

        Args:
            serial_number: Serial number of the AC system
            fan_mode: The fan mode (e.g., "AUTO", "LOW", "MEDIUM", "HIGH")
            continuous: Whether to enable continuous fan mode

        Returns:
            Command response
        """
        command = CommandBuilder.set_fan_mode(fan_mode, continuous)
        return await self.send_command(serial_number, command)

    async def set_zone(self, serial_number: str, zone_number: int, is_enabled: bool) -> Dict[str, Any]:
        """
        Turn a specific zone ON/OFF.

        Args:
            serial_number: Serial number of the AC system
            zone_number: Zone number to control (starting from 0)
            is_enabled: True to turn ON, False to turn OFF

        Returns:
            Command response
        """
        # Get current zone status
        current_status = await self.get_zone_status(serial_number)

        # Create command
        command = CommandBuilder.set_zone(zone_number, is_enabled, current_status)
        return await self.send_command(serial_number, command)

    async def set_multiple_zones(self, serial_number: str, zone_settings: Dict[int, bool]) -> Dict[str, Any]:
        """
        Set multiple zones ON/OFF in a single command.

        Args:
            serial_number: Serial number of the AC system
            zone_settings: Dictionary where keys are zone numbers and values are True/False

        Returns:
            Command response
        """
        command = CommandBuilder.set_multiple_zones(zone_settings)
        return await self.send_command(serial_number, command)

    async def set_temperature(
        self, serial_number: str, mode: str, temperature: Union[float, Dict[str, float]],
        zone: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Set the temperature for the system or a specific zone.

        Args:
            serial_number: Serial number of the AC system
            mode: The mode ('COOL', 'HEAT', 'AUTO')
            temperature: The temperature to set (float or dict with 'cool' and 'heat' keys)
            zone: Zone number for zone-specific temperature, or None for common zone

        Returns:
            Command response
        """
        if mode.upper() not in ["COOL", "HEAT", "AUTO"]:
            raise ValueError("Invalid mode. Choose from 'COOL', 'HEAT', 'AUTO'.")

        command = CommandBuilder.set_temperature(mode, temperature, zone)
        return await self.send_command(serial_number, command)

    async def set_away_mode(self, serial_number: str, mode: bool = False) -> Dict[str, Any]:
        """
        Set the away mode of the AC system.

        Args:
            serial_number: Serial number of the AC system
            mode: Whether to enable away mode

        Returns:
            Command response
        """
        command = CommandBuilder.set_feature_mode("AwayMode", mode)
        return await self.send_command(serial_number, command)

    async def set_quiet_mode(self, serial_number: str, mode: bool = False) -> Dict[str, Any]:
        """
        Set the quiet mode of the AC system.

        Args:
            serial_number: Serial number of the AC system
            mode: Whether to enable quiet mode

        Returns:
            Command response
        """
        command = CommandBuilder.set_feature_mode("QuietModeEnabled", mode)
        return await self.send_command(serial_number, command)

    async def set_turbo_mode(self, serial_number: str, mode: bool = False) -> Dict[str, Any]:
        """
        Set the turbo mode of the AC system.

        Args:
            serial_number: Serial number of the AC system
            mode: Whether to enable turbo mode

        Returns:
            Command response
        """
        command = CommandBuilder.set_feature_mode("TurboMode.Enabled", mode)
        return await self.send_command(serial_number, command)

    # Status retrieval methods

    async def get_master_model(self, serial_number: str) -> Optional[str]:
        """
        Retrieve the master wall controller model.

        Args:
            serial_number: Serial number of the AC system

        Returns:
            The master wall controller model
        """
        return await self._handle_request(self._get_master_model, serial_number)

    async def _get_master_model(self, serial_number: str) -> Optional[str]:
        """Fetch the Master WC Model for the specified AC system."""
        status = await self.get_ac_status(serial_number)
        return (
            status.get("lastKnownState", {})
            .get("AirconSystem", {})
            .get("MasterWCModel")
        )

    async def get_master_serial(self, serial_number: str) -> Optional[str]:
        """
        Retrieve the master wall controller serial number.

        Args:
            serial_number: Serial number of the AC system

        Returns:
            The master wall controller serial number
        """
        return await self._handle_request(self._get_master_serial, serial_number)

    async def _get_master_serial(self, serial_number: str) -> Optional[str]:
        """Fetch the Master serial for the specified AC system."""
        status = await self.get_ac_status(serial_number)
        return (
            status.get("lastKnownState", {})
            .get("AirconSystem", {})
            .get("MasterSerial")
        )

    async def get_master_firmware(self, serial_number: str) -> Optional[str]:
        """
        Retrieve the master wall controller firmware version.

        Args:
            serial_number: Serial number of the AC system

        Returns:
            The master firmware version
        """
        return await self._handle_request(self._get_master_firmware, serial_number)

    async def _get_master_firmware(self, serial_number: str) -> Optional[str]:
        """Fetch the Master firmware version for the specified AC system."""
        status = await self.get_ac_status(serial_number)
        return (
            status.get("lastKnownState", {})
            .get("AirconSystem", {})
            .get("MasterWCFirmwareVersion")
        )

    async def get_outdoor_unit_model(self, serial_number: str) -> Optional[str]:
        """
        Retrieve the outdoor unit model.

        Args:
            serial_number: Serial number of the AC system

        Returns:
            The outdoor unit model
        """
        return await self._handle_request(self._get_outdoor_unit_model, serial_number)

    async def _get_outdoor_unit_model(self, serial_number: str) -> Optional[str]:
        """Fetch the outdoor unit model for the specified AC system."""
        status = await self.get_ac_status(serial_number)
        aircon_system = status.get("lastKnownState", {}).get("AirconSystem", {})
        outdoor_unit = aircon_system.get("OutdoorUnit")

        # Handle the case where OutdoorUnit might be None
        if outdoor_unit is None:
            return None

        return outdoor_unit.get("ModelNumber")

    async def get_status(self, serial_number: str) -> Dict[str, Any]:
        """
        Retrieve the status of the AC system, including zones and other components.

        Args:
            serial_number: Serial number of the AC system

        Returns:
            Full status of the AC system
        """
        return await self._handle_request(self._get_status, serial_number)

    async def _get_status(self, serial_number: str) -> Dict[str, Any]:
        """Fetch the full status of the specified AC system."""
        return await self.get_ac_status(serial_number)

    async def get_zones(self, serial_number: str) -> List[Dict[str, Any]]:
        """
        Retrieve zone information.

        Args:
            serial_number: Serial number of the AC system

        Returns:
            List of zones
        """
        return await self._handle_request(self._get_zones, serial_number)

    async def _get_zones(self, serial_number: str) -> List[Dict[str, Any]]:
        """Fetch zone information for the specified AC system."""
        status = await self.get_ac_status(serial_number)
        return status.get("lastKnownState", {}).get("RemoteZoneInfo", [])

    async def get_zone_status(self, serial_number: str) -> List[bool]:
        """
        Retrieve zone status (enabled/disabled states).

        Args:
            serial_number: Serial number of the AC system

        Returns:
            List of boolean values indicating zone states
        """
        return await self._handle_request(self._get_zone_status, serial_number)

    async def _get_zone_status(self, serial_number: str) -> List[bool]:
        """Fetch zone enabled/disabled status for the specified AC system."""
        status = await self.get_ac_status(serial_number)
        return status.get("lastKnownState", {}).get("UserAirconSettings", {}).get("EnabledZones", [])

    # Status update methods

    async def update_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the updated status of all AC systems.

        Returns:
            Dictionary of system statuses by serial number
        """
        if not self.systems:
            return {}

        results = {}
        for system in self.systems:
            serial = system.get("serial")

            # Check if we need a full update or incremental update
            if serial not in self.state_manager.latest_event_id:
                await self._handle_request(self._fetch_full_update, serial)
            else:
                await self._handle_request(self._fetch_incremental_updates, serial)

            # Store the result
            status = self.state_manager.get_status(serial)
            if status:
                results[serial] = status.dict()

        return results

    async def _fetch_full_update(self, serial_number: str) -> Optional[ActronAirNeoStatus]:
        """Fetch the full update for a system."""
        _LOGGER.debug("Fetching full-status-broadcast")
        try:
            events = await self.get_ac_events(serial_number, event_type="latest")
            if not events:
                _LOGGER.error("Failed to fetch events: get_ac_events returned None")
                return None

            return self.state_manager.process_events(serial_number, events)
        except (TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Error fetching full update: %s", e)
            return None

    async def _fetch_incremental_updates(self, serial_number: str) -> Optional[ActronAirNeoStatus]:
        """Fetch incremental updates since the last event."""
        _LOGGER.debug("Fetching incremental updates")
        try:
            latest_event_id = self.state_manager.latest_event_id.get(serial_number)
            events = await self.get_ac_events(
                serial_number,
                event_type="newer",
                event_id=latest_event_id
            )
            if not events:
                _LOGGER.error("Failed to fetch events: get_ac_events returned None")
                return None

            return self.state_manager.process_events(serial_number, events)
        except (TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Error fetching incremental updates: %s", e)
            return None

    # Property accessors

    @property
    def access_token(self) -> Optional[str]:
        """Get the current access token."""
        return self.oauth2_auth.access_token

    @property
    def refresh_token_value(self) -> Optional[str]:
        """Get the current refresh token."""
        return self.oauth2_auth.refresh_token

    @property
    def pairing_token(self) -> Optional[str]:
        """Get the current pairing token (for backward compatibility)."""
        return self.oauth2_auth.refresh_token

    @pairing_token.setter
    def pairing_token(self, value: str) -> None:
        """Set the pairing token (for backward compatibility)."""
        self.oauth2_auth.refresh_token = value

    @property
    def status(self) -> Dict[str, Dict[str, Any]]:
        """Get the current status of all systems."""
        return {
            serial: status.dict()
            for serial, status in self.state_manager.status.items()
        }

    @property
    def latest_event_id(self) -> Dict[str, str]:
        """Get the latest event ID for each system."""
        return self.state_manager.latest_event_id.copy()
