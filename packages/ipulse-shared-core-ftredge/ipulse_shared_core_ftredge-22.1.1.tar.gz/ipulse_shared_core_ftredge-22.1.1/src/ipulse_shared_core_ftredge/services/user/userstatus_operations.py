"""
Userstatus Operations - CRUD operations for Userstatus
"""
import os
import logging
from typing import Dict, Any, Optional

from google.cloud import firestore
from pydantic import ValidationError as PydanticValidationError

from ...models import UserStatus
from ...exceptions import ResourceNotFoundError, UserStatusError
from ..base import BaseFirestoreService


class UserstatusOperations:
    """
    Handles CRUD operations for Userstatus documents
    """

    def __init__(
        self,
        firestore_client: firestore.Client,
        logger: Optional[logging.Logger] = None,
        timeout: float = 10.0,
        status_collection: Optional[str] = None
    ):
        self.db = firestore_client
        self.logger = logger or logging.getLogger(__name__)
        self.timeout = timeout

        self.status_collection_name = status_collection or UserStatus.get_collection_name()

        # Archival configuration
        self.archive_userstatus_on_delete = os.getenv('ARCHIVE_USERSTATUS_ON_DELETE', 'true').lower() == 'true'
        self.archive_userstatus_collection_name = os.getenv(
            'ARCHIVE_USERSTATUS_COLLECTION_NAME',
            "~archive_core_user_userstatuss"
        )

        # Initialize DB service
        self._status_db_service = BaseFirestoreService[UserStatus](
            db=self.db,
            collection_name=self.status_collection_name,
            resource_type=UserStatus.OBJ_REF,
            model_class=UserStatus,
            logger=self.logger,
            timeout=self.timeout
        )

    async def get_userstatus(self, user_uid: str, convert_to_model: bool = True) -> Optional[UserStatus]:
        """Retrieve a user status by UID"""
        userstatus_id = f"{UserStatus.OBJ_REF}_{user_uid}"

        try:
            userstatus = await self._status_db_service.get_document(
                userstatus_id,
                convert_to_model=convert_to_model
            )
            if userstatus:
                self.logger.debug("Successfully retrieved user status for %s", user_uid)
                # Always return a UserStatus model to match the return type
                if isinstance(userstatus, dict):
                    return UserStatus(**userstatus)
                return userstatus
            else:
                self.logger.debug("User status not found for %s", user_uid)
                return None

        except ResourceNotFoundError:
            self.logger.debug("User status not found for %s", user_uid)
            return None
        except Exception as e:
            self.logger.error("Failed to fetch user status for %s: %s", user_uid, str(e), exc_info=True)
            raise UserStatusError(
                detail=f"Failed to fetch user status: {str(e)}",
                user_uid=user_uid,
                operation="get_userstatus",
                original_error=e
            ) from e

    async def create_userstatus(self, userstatus: UserStatus, creator_uid: Optional[str] = None) -> UserStatus:
        """Create a new user status"""
        self.logger.info(f"Creating user status for UID: {userstatus.user_uid}")
        try:
            doc_id = f"{UserStatus.OBJ_REF}_{userstatus.user_uid}"
            effective_creator_uid = creator_uid or userstatus.user_uid
            await self._status_db_service.create_document(doc_id, userstatus, effective_creator_uid)
            self.logger.info("Successfully created user status for UID: %s", userstatus.user_uid)
            return userstatus
        except Exception as e:
            self.logger.error("Error creating user status for %s: %s", userstatus.user_uid, e, exc_info=True)
            raise UserStatusError(
                detail=f"Failed to create user status: {str(e)}",
                user_uid=userstatus.user_uid,
                operation="create_userstatus",
                original_error=e
            ) from e

    async def update_userstatus(self, user_uid: str, status_data: Dict[str, Any], updater_uid: str) -> UserStatus:
        """Update a user status"""
        userstatus_id = f"{UserStatus.OBJ_REF}_{user_uid}"

        # Remove system fields that shouldn't be updated
        update_data = status_data.copy()
        update_data.pop('user_uid', None)
        update_data.pop('id', None)
        update_data.pop('created_at', None)
        update_data.pop('created_by', None)

        try:
            updated_doc_dict = await self._status_db_service.update_document(
                userstatus_id,
                update_data,
                updater_uid=updater_uid
            )
            self.logger.info("Userstatus for %s updated successfully by %s", user_uid, updater_uid)
            return UserStatus(**updated_doc_dict)
        except ResourceNotFoundError as exc:
            raise UserStatusError(
                detail="User status not found",
                user_uid=user_uid,
                operation="update_userstatus"
            ) from exc
        except Exception as e:
            self.logger.error("Error updating Userstatus for %s: %s", user_uid, str(e), exc_info=True)
            raise UserStatusError(
                detail=f"Failed to update user status: {str(e)}",
                user_uid=user_uid,
                operation="update_userstatus",
                original_error=e
            ) from e

    async def delete_userstatus(self, user_uid: str, updater_uid: str = "system_deletion", archive: Optional[bool] = True) -> bool:
        """Delete (archive and delete) user status"""
        status_doc_id = f"{UserStatus.OBJ_REF}_{user_uid}"
        should_archive = archive if archive is not None else self.archive_userstatus_on_delete

        try:
            # Get status data for archival
            status_data = await self._status_db_service.get_document(status_doc_id, convert_to_model=False)

            if status_data:
                # Ensure we have a dict for archival
                status_dict = status_data if isinstance(status_data, dict) else status_data.__dict__

                # Archive if enabled
                if should_archive:
                    await self._status_db_service.archive_document(
                        document_data=status_dict,
                        doc_id=status_doc_id,
                        archive_collection=self.archive_userstatus_collection_name,
                        archived_by=updater_uid
                    )

                # Delete the original document
                await self._status_db_service.delete_document(status_doc_id)
                self.logger.info("Successfully deleted user status: %s", status_doc_id)
                return True
            else:
                self.logger.warning("User status %s not found for deletion", status_doc_id)
                return True  # Consider non-existent as successfully deleted

        except ResourceNotFoundError:
            self.logger.debug("User status %s not found for deletion (idempotent)", status_doc_id)
            return True  # Idempotent - already "deleted"
        except Exception as e:
            self.logger.error("Failed to delete user status %s: %s", status_doc_id, str(e), exc_info=True)
            raise UserStatusError(
                detail=f"Failed to delete user status: {str(e)}",
                user_uid=user_uid,
                operation="delete_userstatus",
                original_error=e
            ) from e

    async def validate_userstatus_data(
        self,
        status_data: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, list[str]]:
        """Validate user status data without creating documents"""
        errors = []
        if status_data:
            try:
                UserStatus(**status_data)
            except PydanticValidationError as e:
                errors.append(f"Status validation error: {str(e)}")
        return len(errors) == 0, errors

    async def validate_and_cleanup_user_permissions(
        self, user_uid: str, updater_uid: str, delete_expired: bool = True
    ) -> int:
        """Validate and clean up expired IAM permissions for a user."""
        userstatus = await self.get_userstatus(user_uid)
        if not userstatus:
            self.logger.warning("Userstatus not found for %s, cannot validate permissions.", user_uid)
            return 0

        removed_count = userstatus.cleanup_expired_permissions()

        if removed_count > 0 and delete_expired:
            await self.update_userstatus(
                user_uid,
                userstatus.model_dump(exclude_none=True),
                updater_uid=updater_uid
            )
            self.logger.info("Removed %d expired permissions for user %s.", removed_count, user_uid)

        return removed_count

    async def userstatus_exists(self, user_uid: str) -> bool:
        """Check if a user status exists."""
        return await self._status_db_service.document_exists(f"{UserStatus.OBJ_REF}_{user_uid}")
