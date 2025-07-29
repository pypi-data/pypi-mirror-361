import base64
import json
import secrets
import urllib.parse
from abc import ABC
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from abs_exception_core.exceptions import InternalServerError
from abs_utils.logger import setup_logger
from fastapi import HTTPException

from abs_integration_core.schema import Subscription

logger = setup_logger(__name__)


class SharepointIntegrationBaseService(ABC):
    def get_auth_url(self, state: Optional[Dict] = None) -> Dict[str, str]:
        """
        Generate an authentication URL for Microsoft SharePoint OAuth flow.
        Returns both the auth URL and the state for verification.

        Args:
            state: Optional state dictionary to include in the OAuth flow
        """
        # Generate CSRF token
        csrf_token = secrets.token_urlsafe(16)

        # Prepare state parameter
        state_param = csrf_token
        if state:
            try:
                # Convert state dict to JSON and URL encode it
                state_json = json.dumps(state)
                state_param = urllib.parse.quote(state_json)
            except Exception as e:
                raise InternalServerError(f"Error encoding state: {e}")

        auth_url = (
            f"{self.authority}/oauth2/v2.0/authorize?"
            f"client_id={self.client_id}&"
            f"response_type=code&"
            f"redirect_uri={self.redirect_url}&"
            f"scope={self.scopes}&"
            f"state={state_param}"
        )

        return {"auth_url": auth_url, "state": state_param}

    async def subscribe(
        self,
        user_id: int,
        target_url: str,
        site_id: str,
        resource_id: str,
        expiration_days: int = 3,
        *args,
        **kwargs,
    ) -> Subscription:
        """
        Subscribe to a resource.
        """
        if not resource_id:
            raise ValueError("Resource ID is required")
        if not site_id:
            raise ValueError("Site ID is required")

        subscription = await self.create_subscription(
            user_id=user_id,
            resource=f"/sites/{site_id}/lists/{resource_id}",
            expiration_days=expiration_days,
            target_url=target_url,
        )

        return subscription

    async def create_subscription(
        self,
        user_id: int,
        resource: str,
        target_url: str,
        expiration_days: int = 3,
    ) -> Dict:
        """
        Create a subscription for SharePoint list or folder changes.

        Args:
            resource: The resource path (e.g., "/sites/{site-id}/lists/{list-id}")
            change_type: Types of changes to monitor (created,updated,deleted)
            expiration_days: Number of days until subscription expires (max 3)

        Returns:
            Dict containing subscription details
        """
        # Get valid access token
        token_data = await self.get_integration_tokens(user_id)

        # Calculate expiration time (max 3 days from now)
        expiration = datetime.now(UTC) + timedelta(days=min(expiration_days, 3))

        client_state = secrets.token_urlsafe(16)
        subscription_data = {
            "changeType": "updated",
            "notificationUrl": target_url,
            "resource": resource,
            "expirationDateTime": expiration.isoformat(),
            "clientState": client_state,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.graph_api_url}/subscriptions",
                headers={"Authorization": f"Bearer {token_data.access_token}"},
                json=subscription_data,
            )
            if response.status_code >= 400:
                logger.error(f"Graph API error: {response.text}")
            response.raise_for_status()
            return response.json()

    async def renew_subscription(
        self, subscription_id: str, expiration_days: int = 3
    ) -> Dict:
        """
        Renew an existing subscription.

        Args:
            subscription_id: The ID of the subscription to renew
            expiration_days: Number of days until subscription expires (max 3)

        Returns:
            Dict containing updated subscription details
        """
        token_data = await self.get_integration_tokens()
        expiration = datetime.now(UTC) + timedelta(days=min(expiration_days, 3))

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.graph_api_url}/subscriptions/{subscription_id}",
                headers={"Authorization": f"Bearer {token_data.access_token}"},
                json={"expirationDateTime": expiration.isoformat()},
            )
            response.raise_for_status()
            return response.json()

    async def delete_subscription(self, subscription_id: str, user_id: int) -> None:
        """
        Delete a subscription.

        Args:
            subscription_id: The ID of the subscription to delete
        """
        token_data = await self.get_integration_tokens(user_id)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.graph_api_url}/subscriptions/{subscription_id}",
                    headers={"Authorization": f"Bearer {token_data.access_token}"},
                )
                response.raise_for_status()

        except Exception as e:
            logger.error(f"Error deleting subscription: {str(e)}")

            if "Client error" in str(e):
                if "404 Not Found" in str(e):
                    logger.info(f"Subscription with id {subscription_id} not found")
            else:
                raise e

    async def list_subscriptions(
        self, user_id: int, page: int = 1, page_size: int = 10, *args, **kwargs
    ) -> Dict:
        """
        List all webhook subscriptions for the DocuSign account using direct API calls.

        Returns:
            Dictionary containing list of subscriptions and their details
        """
        return await self.subscription_service.list_subscriptions(
            self.provider_name, user_id, page, page_size
        )

    async def get_sites(
        self, user_id: int, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all SharePoint sites or search for specific sites.

        Args:
            search: Optional search term to filter sites

        Returns:
            List of site information
        """
        token_data = await self.get_integration_tokens(user_id)
        if search:
            url = f"{self.graph_api_url}/sites?search={search}"
        else:
            # Use a default keyword to return all sites (e.g., 'sharepoint')
            url = f"{self.graph_api_url}/sites?search=sharepoint"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, headers={"Authorization": f"Bearer {token_data.access_token}"}
            )
            response.raise_for_status()
            return response.json().get("value", [])

    async def get_drive_folders(
        self, user_id: int, site_id: str, drive_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all folders in a SharePoint drive.

        Args:
            site_id: The ID of the SharePoint site
            drive_id: The ID of the drive

        Returns:
            List of folder information
        """
        token_data = await self.get_integration_tokens(user_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.graph_api_url}/sites/{site_id}/drives/{drive_id}/root/children",
                headers={"Authorization": f"Bearer {token_data.access_token}"},
            )
            response.raise_for_status()
            return [
                item
                for item in response.json().get("value", [])
                if item.get("folder") is not None
            ]

    async def get_site_drives(self, user_id: int, site_id: str) -> List[Dict[str, Any]]:
        """
        Get all drives in a SharePoint site.

        Args:
            site_id: The ID of the SharePoint site

        Returns:
            List of drive information
        """
        token_data = await self.get_integration_tokens(user_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.graph_api_url}/sites/{site_id}/drives",
                headers={"Authorization": f"Bearer {token_data.access_token}"},
            )
            response.raise_for_status()
            return response.json().get("value", [])

    async def get_site_lists(self, user_id: int, site_id: str) -> List[Dict[str, Any]]:
        """
        Get all lists in a SharePoint site.

        Args:
            site_id: The ID of the SharePoint site

        Returns:
            List of list information
        """
        token_data = await self.get_integration_tokens(user_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.graph_api_url}/sites/{site_id}/lists",
                headers={"Authorization": f"Bearer {token_data.access_token}"},
            )
            response.raise_for_status()
            return response.json().get("value", [])

    async def get_drive_items(
        self,
        user_id: int,
        site_id: str,
        drive_id: str,
        folder_path: Optional[str] = None,
        page_token: Optional[str] = None,
        page_size: int = 40,
    ) -> Dict[str, Any]:
        """
        Get items (files and folders) in a SharePoint drive or specific folder with pagination.

        Args:
            user_id: The ID of the user
            site_id: The ID of the SharePoint site
            drive_id: The ID of the drive
            folder_path: Optional path to a specific folder (e.g., "/Documents/SubFolder")
            page_token: Optional pagination token for next page
            page_size: Number of items per page (default: 40)

        Returns:
            Dictionary containing items and pagination metadata
        """
        token_data = await self.get_integration_tokens(user_id)

        # Build the URL based on whether we're browsing root or a specific folder
        if folder_path:
            # Remove leading slash if present and encode the path
            folder_path = folder_path.lstrip("/")
            encoded_path = urllib.parse.quote(folder_path)
            url = f"{self.graph_api_url}/sites/{site_id}/drives/{drive_id}/root:/{encoded_path}:/children"
        else:
            url = (
                f"{self.graph_api_url}/sites/{site_id}/drives/{drive_id}/root/children"
            )

        # Add pagination parameters
        params = {"$top": page_size, "$orderby": "name"}

        if page_token:
            # Use $skiptoken for Graph API pagination
            params["$skiptoken"] = page_token

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token_data.access_token}"},
                params=params,
            )
            response.raise_for_status()

            response_data = response.json()
            items = response_data.get("value", [])
            next_link = response_data.get("@odata.nextLink")

            # Process items to add useful metadata
            processed_items = []
            for item in items:
                processed_item = {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "type": "folder" if item.get("folder") else "file",
                    "size": item.get("size", 0),
                    "webUrl": item.get("webUrl"),
                    "createdDateTime": item.get("createdDateTime"),
                    "lastModifiedDateTime": item.get("lastModifiedDateTime"),
                    "parentReference": item.get("parentReference", {}),
                }

                # Add folder-specific metadata
                if item.get("folder"):
                    processed_item["childCount"] = item.get("folder", {}).get(
                        "childCount", 0
                    )
                    processed_item["canSubscribe"] = (
                        True  # Folders can be subscribed to via drive subscription
                    )

                # Add file-specific metadata
                elif item.get("file"):
                    processed_item["mimeType"] = item.get("file", {}).get("mimeType")
                    processed_item["canSubscribe"] = (
                        False  # Individual files cannot be subscribed to
                    )

                processed_items.append(processed_item)

            # Generate next page token
            next_page_token = None
            if next_link:
                # Extract skiptoken from the @odata.nextLink URL
                try:
                    parsed_url = urllib.parse.urlparse(next_link)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    next_page_token = query_params.get("$skiptoken", [None])[0]
                    logger.debug(f"Extracted skiptoken: {next_page_token}")
                except Exception as e:
                    logger.error(f"Failed to extract skiptoken from next link: {e}")
                    next_page_token = None

            return {
                "items": processed_items,
                "nextPageToken": next_page_token,
                "hasNextPage": next_page_token is not None,
                "totalCount": len(processed_items),
            }

    async def get_folder_by_path(
        self, user_id: int, site_id: str, drive_id: str, folder_path: str
    ) -> Dict[str, Any]:
        """
        Get information about a specific folder by its path.

        Args:
            user_id: The ID of the user
            site_id: The ID of the SharePoint site
            drive_id: The ID of the drive
            folder_path: Path to the folder (e.g., "/Documents/SubFolder")

        Returns:
            Dictionary containing folder information
        """
        token_data = await self.get_integration_tokens(user_id)

        # Remove leading slash if present and encode the path
        folder_path = folder_path.lstrip("/")
        encoded_path = urllib.parse.quote(folder_path)
        url = f"{self.graph_api_url}/sites/{site_id}/drives/{drive_id}/root:/{encoded_path}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, headers={"Authorization": f"Bearer {token_data.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def list_resources(
        self,
        user_id: int,
        site_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        folder_path: Optional[str] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List available SharePoint resources with dynamic browsing functionality and pagination.

        Navigation levels:
        1. No parameters: List all sites and their drives/lists
        2. site_id only: List drives in the site
        3. site_id + resource_id: List items in the list (with pagination, 40 items per page)
        4. site_id + resource_id + folder_path: List items in the specific folder (with pagination, 40 items per page)

        Args:
            user_id: The ID of the user
            site_id: Optional site ID to browse
            resource_id: Optional resource ID (list_id) to browse
            folder_path: Optional folder path to browse
            page_token: Optional base64-encoded pagination token containing navigation state and Microsoft Graph skiptoken

        Returns:
            Dictionary containing resources, navigation metadata, and pagination info with next page token
        """
        try:
            # Handle pagination token if provided
            current_page_token = None
            if page_token:
                logger.info(f"Processing pagination token: {page_token}")
                try:
                    # Decode the page token to get navigation state and pagination info
                    decoded_token = base64.b64decode(page_token).decode("utf-8")
                    token_data = json.loads(decoded_token)

                    # Extract navigation state from token
                    site_id = token_data.get("site_id", site_id)
                    resource_id = token_data.get("resource_id", resource_id)
                    folder_path = token_data.get("folder_path", folder_path)
                    current_page_token = token_data.get("page_token")

                    logger.info(
                        f"Decoded navigation state: site_id={site_id}, resource_id={resource_id}, folder_path={folder_path}, page_token={current_page_token}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to decode page token: {e}, using default navigation"
                    )

            # Level 1: No parameters - List all sites and their drives/lists
            if not site_id:
                logger.info("Listing all SharePoint sites and their drives/lists")
                sites = await self.get_sites(user_id)

                resources = []
                for site in sites:
                    try:
                        site_id = site["id"].split(",")[1]
                        
                        # Get both drives and lists for the site
                        drives = await self.get_site_drives(user_id, site_id)
                        lists = await self.get_site_lists(user_id, site_id)
                        
                        logger.debug(
                            f"Found {len(drives)} drives and {len(lists)} lists for site {site.get('name', 'Unknown')}"
                        )

                        # Create a mapping of drive names to list IDs for matching
                        # Check both 'name' and 'displayName' fields for lists
                        lists_by_name = {}
                        for list_item in lists:
                            list_name = list_item.get("name", "").lower()
                            list_display_name = list_item.get("displayName", "").lower()
                            list_id = list_item["id"]
                            
                            # Map both name and displayName to the same list ID
                            lists_by_name[list_name] = list_id
                            if list_display_name and list_display_name != list_name:
                                lists_by_name[list_display_name] = list_id

                        # Add each drive as a resource, including matching list ID if found
                        for drive in drives:
                            drive_name = drive.get("name", "").lower()
                            matching_list_id = lists_by_name.get(drive_name)
                            
                            navigation_path = {
                                "site_id": site_id,
                            }
                            
                            # Add list_id to navigationPath if there's a matching list
                            if matching_list_id:
                                navigation_path["resource_id"] = matching_list_id
                            
                            drive_info = {
                                "id": drive["id"],
                                "name": f"{site.get('name', 'Unknown Site')} - {drive.get('name', 'Unknown Drive')}",
                                "webUrl": drive.get("webUrl"),
                                "description": f"Drive in {site.get('name', 'Unknown Site')}" + (f" (has matching list: {matching_list_id})" if matching_list_id else ""),
                                "type": "drive",
                                "navigationPath": navigation_path
                            }
                            resources.append(drive_info)

                    except Exception as e:
                        logger.error(
                            f"Error getting drives/lists for site {site.get('name', 'Unknown')}: {e}"
                        )
                        # Still add the site even if we can't get drives/lists
                        site_info = {
                            "id": site_id,
                            "name": site.get("name", "Unknown Site"),
                            "webUrl": site.get("webUrl"),
                            "description": site.get("description", ""),
                            "navigationPath": {"site_id": site_id},
                        }
                        resources.append(site_info)

                return {
                    "resources": resources,
                    "totalCount": len(resources),
                    "pagination": {"hasNextPage": False, "nextPageToken": None},
                }

            # Level 2: site_id only - List drives in the site
            elif site_id and not resource_id:
                logger.info(f"Listing drives for site: {site_id}")
                drives = await self.get_site_drives(user_id, site_id)
                lists = await self.get_site_lists(user_id, site_id)

                # Create a mapping of drive names to list IDs for matching
                lists_by_name = {}
                for list_item in lists:
                    list_name = list_item.get("name", "").lower()
                    list_display_name = list_item.get("displayName", "").lower()
                    list_id = list_item["id"]
                    
                    # Map both name and displayName to the same list ID
                    lists_by_name[list_name] = list_id
                    if list_display_name and list_display_name != list_name:
                        lists_by_name[list_display_name] = list_id

                resources = []
                for drive in drives:
                    drive_name = drive.get("name", "").lower()
                    matching_list_id = lists_by_name.get(drive_name)
                    
                    navigation_path = {"site_id": site_id}
                    if matching_list_id:
                        navigation_path["resource_id"] = matching_list_id
                    
                    drive_info = {
                        "id": drive["id"],
                        "name": drive.get("name", "Unknown Drive"),
                        "webUrl": drive.get("webUrl"),
                        "description": drive.get("description", ""),
                        "navigationPath": navigation_path,
                    }
                    resources.append(drive_info)

                return {
                    "resources": resources,
                    "totalCount": len(resources),
                    "pagination": {"hasNextPage": False, "nextPageToken": None},
                }

            # Level 3 & 4: site_id + resource_id - List items in drive/folder
            elif site_id and resource_id:
                # Find the corresponding drive_id from the resource_id (list_id)
                drives = await self.get_site_drives(user_id, site_id)
                lists = await self.get_site_lists(user_id, site_id)
                
                # Create mapping from list_id to drive_id
                drive_id = None
                for list_item in lists:
                    if list_item["id"] == resource_id:
                        list_name = list_item.get("displayName", list_item.get("name", "")).lower()
                        for drive in drives:
                            if drive.get("name", "").lower() == list_name:
                                drive_id = drive["id"]
                                break
                        break
                
                if not drive_id:
                    logger.error(f"Could not find corresponding drive for resource_id: {resource_id}")
                    return {
                        "resources": [],
                        "totalCount": 0,
                        "pagination": {"hasNextPage": False, "nextPageToken": None},
                    }

                if folder_path:
                    logger.info(
                        f"Listing items in folder: {folder_path} (resource: {resource_id})"
                    )
                else:
                    logger.info(f"Listing items in drive root: {resource_id}")

                items_result = await self.get_drive_items(
                    user_id,
                    site_id=site_id,
                    drive_id=drive_id,
                    folder_path=folder_path,
                    page_token=current_page_token,
                    page_size=2,
                )

                items = items_result["items"]
                next_page_token = items_result["nextPageToken"]
                has_next_page = items_result["hasNextPage"]

                resources = []
                for item in items:
                    if item["type"] == "folder":
                        item_folder_path = (
                            f"{folder_path}/{item['name']}"
                            if folder_path
                            else item["name"]
                        )
                        navigation_path = {
                            "site_id": site_id,
                            "resource_id": resource_id,
                            "folder_path": item_folder_path,
                        }
                        has_children = item.get("childCount", 0) > 0
                    else:
                        navigation_path = None
                        has_children = False

                    item_info = {
                        "id": item["id"],
                        "name": item["name"],
                        "type": item["type"],
                        "size": item.get("size", 0),
                        "webUrl": item.get("webUrl"),
                        "createdDateTime": item.get("createdDateTime"),
                        "lastModifiedDateTime": item.get("lastModifiedDateTime"),
                        "mimeType": item.get("mimeType"),
                        "canSubscribe": item["type"] == "folder",
                        "hasChildren": has_children,
                        "navigationPath": navigation_path,
                    }
                    resources.append(item_info)

                # Generate next page token for pagination
                next_page_token_encoded = None
                if has_next_page and next_page_token:
                    # Encode navigation state and pagination info
                    token_data = {
                        "site_id": site_id,
                        "resource_id": resource_id,
                        "folder_path": folder_path,
                        "page_token": next_page_token,
                    }
                    next_page_token_encoded = base64.b64encode(
                        json.dumps(token_data).encode("utf-8")
                    ).decode("utf-8")

                return {
                    "resources": resources,
                    "totalCount": len(resources),
                    "currentPath": folder_path or "",
                    "pagination": {
                        "hasNextPage": has_next_page,
                        "nextPageToken": next_page_token_encoded,
                    },
                }

            else:
                raise ValueError("Invalid parameter combination")

        except Exception as e:
            logger.error(f"Error listing SharePoint resources: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to list SharePoint resources: {str(e)}"
            )
