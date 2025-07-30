"""
usertype Catalog Service

This service manages usertype templates stored in Firestore.
These templates are used to configure default settings for user profiles and statuses.
"""

import logging
from typing import Dict, List, Optional, Any
from google.cloud.firestore import Client
from ipulse_shared_base_ftredge import IAMUserType
from ipulse_shared_base_ftredge.enums.enums_status import ObjectOverallStatus
from ipulse_shared_core_ftredge.models.catalog.usertype import UserType
from ipulse_shared_core_ftredge.services.base.base_firestore_service import BaseFirestoreService

class CatalogUserTypeService(BaseFirestoreService[UserType]):
    """
    Service for managing usertype catalog configurations.

    This service provides CRUD operations for usertype templates that define
    the default settings and permissions for different usertypes.
    """

    def __init__(
        self,
        firestore_client: Client,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the usertype Catalog Service.

        Args:
            firestore_client: Firestore client instance
            logger: Logger instance (optional)
        """
        super().__init__(
            db=firestore_client,
            collection_name="papp_core_catalog_usertypes",
            resource_type="usertype",
            model_class=UserType,
            logger=logger or logging.getLogger(__name__)
        )
        self.archive_collection_name = "~archive_papp_core_catalog_usertypes"

    async def create_usertype(
        self,
        usertype_id: str,
        user_type: UserType,
        creator_uid: str
    ) -> UserType:
        """
        Create a new usertype.

        Args:
            usertype_id: Unique identifier for the usertype
            user_type: Usertype data
            creator_uid: UID of the user creating the usertype

        Returns:
            Created usertype

        Raises:
            ServiceError: If creation fails
            ValidationError: If usertype data is invalid
        """
        self.logger.info(f"Creating usertype: {usertype_id}")

        # Create the document
        created_doc = await self.create_document(
            doc_id=usertype_id,
            data=user_type,
            creator_uid=creator_uid
        )

        # Convert back to model
        result = UserType.model_validate(created_doc)
        self.logger.info(f"Successfully created usertype: {usertype_id}")
        return result

    async def get_usertype(self, usertype_id: str) -> Optional[UserType]:
        """
        Retrieve a usertype by ID.

        Args:
            usertype_id: Unique identifier for the usertype

        Returns:
            usertype if found, None otherwise

        Raises:
            ServiceError: If retrieval fails
        """
        self.logger.debug(f"Retrieving usertype: {usertype_id}")
        doc_data = await self.get_document(usertype_id)
        if doc_data is None:
            return None
        return UserType.model_validate(doc_data) if isinstance(doc_data, dict) else doc_data

    async def update_usertype(
        self,
        usertype_id: str,
        updates: Dict[str, Any],
        updater_uid: str
    ) -> UserType:
        """
        Update a usertype.

        Args:
            usertype_id: Unique identifier for the usertype
            updates: Fields to update
            updater_uid: UID of the user updating the usertype

        Returns:
            Updated usertype

        Raises:
            ServiceError: If update fails
            ResourceNotFoundError: If usertype not found
            ValidationError: If update data is invalid
        """
        self.logger.info(f"Updating usertype: {usertype_id}")

        updated_doc = await self.update_document(
            doc_id=usertype_id,
            update_data=updates,
            updater_uid=updater_uid
        )

        result = UserType.model_validate(updated_doc)
        self.logger.info(f"Successfully updated usertype: {usertype_id}")
        return result

    async def delete_usertype(
        self,
        usertype_id: str,
        archive: bool = True
    ) -> bool:
        """
        Delete a usertype.

        Args:
            usertype_id: Unique identifier for the usertype
            archive: Whether to archive the usertype before deletion

        Returns:
            True if deletion was successful

        Raises:
            ServiceError: If deletion fails
            ResourceNotFoundError: If usertype not found
        """
        self.logger.info(f"Deleting usertype: {usertype_id}")

        if archive:
            # Get the usertype data before deletion for archiving
            template = await self.get_usertype(usertype_id)
            if template:
                await self.archive_document(
                    document_data=template.model_dump(),
                    doc_id=usertype_id,
                    archive_collection=self.archive_collection_name,
                    archived_by="system"
                )

        result = await self.delete_document(usertype_id)
        self.logger.info(f"Successfully deleted usertype: {usertype_id}")
        return result

    async def list_usertypes(
        self,
        primary_usertype: Optional[IAMUserType] = None,
        pulse_status: Optional[ObjectOverallStatus] = None,
        latest_version_only: bool = False,
        limit: Optional[int] = None
    ) -> List[UserType]:
        """
        List usertypes with optional filtering.

        Args:
            primary_usertype: Filter by specific primary usertype
            pulse_status: Filter by specific pulse status
            latest_version_only: Only return the latest version per usertype
            limit: Maximum number of usertypes to return

        Returns:
            List of usertypes

        Raises:
            ServiceError: If listing fails
        """
        self.logger.debug(f"Listing usertypes - primary_usertype: {primary_usertype}, pulse_status: {pulse_status}, latest_version_only: {latest_version_only}")

        # Build query filters
        filters = []
        if primary_usertype:
            filters.append(("primary_usertype", "==", primary_usertype.value))
        if pulse_status:
            filters.append(("pulse_status", "==", pulse_status.value))

        # If latest_version_only is requested, order by version descending
        order_by = None
        if latest_version_only:
            order_by = "version"
            # We'll need to group by primary_usertype and take the first from each group
            # This is more complex, so let's handle it differently

        docs = await self.list_documents(
            filters=filters,
            order_by=order_by,
            limit=limit
        )

        # Convert to UserType models
        usertypes = [UserType.model_validate(doc) if isinstance(doc, dict) else doc for doc in docs]

        # If latest_version_only is requested, group by primary_usertype and get highest version
        if latest_version_only:
            # Group by primary_usertype
            usertype_groups = {}
            for usertype in usertypes:
                key = usertype.primary_usertype.value
                if key not in usertype_groups:
                    usertype_groups[key] = []
                usertype_groups[key].append(usertype)

            # Get the latest version for each group
            latest_usertypes = []
            for group in usertype_groups.values():
                if group:
                    # Sort by version descending and take the first
                    latest = max(group, key=lambda x: x.version)
                    latest_usertypes.append(latest)

            return latest_usertypes

        return usertypes

    def _get_collection(self):
        """Get the Firestore collection reference."""
        return self.db.collection(self.collection_name)

    async def usertype_exists(self, usertype_id: str) -> bool:
        """
        Check if a usertype exists.

        Args:
            usertype_id: Unique identifier for the usertype

        Returns:
            True if usertype exists, False otherwise

        Raises:
            ServiceError: If check fails
        """
        return await self.document_exists(usertype_id)

    async def validate_usertype_data(self, usertype_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate usertype data.

        Args:
            usertype_data: Usertype data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            UserType.model_validate(usertype_data)
            return True, []
        except Exception as e:
            return False, [str(e)]


    async def get_default_credits_for_usertype(self, primary_usertype: IAMUserType) -> Dict[str, int]:
        """
        Get default credit settings for a specific usertype.

        Args:
            primary_usertype: The primary usertype

        Returns:
            Dictionary with default credit values

        Raises:
            ServiceError: If retrieval fails
        """
        self.logger.debug(f"Getting default credits for usertype: {primary_usertype}")

        usertypes = await self.list_usertypes(
            primary_usertype=primary_usertype,
            pulse_status=ObjectOverallStatus.ACTIVE,
            latest_version_only=True,
            limit=1
        )
        usertype = usertypes[0] if usertypes else None
        if not usertype:
            self.logger.warning(f"No active usertype found for: {primary_usertype}")
            return {
                "subscription_based_insight_credits": 0,
                "extra_insight_credits": 0,
                "voting_credits": 0
            }

        return {
            "extra_insight_credits": usertype.default_extra_insight_credits,
            "voting_credits": usertype.default_voting_credits
        }
