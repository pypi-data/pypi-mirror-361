"""
User Multistep Operations - Complete user lifecycle operations

Handles complete user creation and deletion operations that span across
Firebase Auth, UserProfile, and UserStatus in coordinated transactions.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple, cast
from ipulse_shared_base_ftredge.enums import ApprovalStatus
from ...models import UserProfile, UserStatus, UserAuth, UserType
from .userauth_operations import UserauthOperations
from .userprofile_operations import UserprofileOperations
from .userstatus_operations import UserstatusOperations
from .user_subscription_operations import UsersubscriptionOperations
from .user_permissions_operations import UserpermissionsOperations
from ..catalog.catalog_usertype_service import CatalogUserTypeService
from ..catalog.catalog_subscriptionplan_service import CatalogSubscriptionPlanService

from ...exceptions import (
    UserCreationError
)


class UsermultistepOperations:
    """
    Handles complete user lifecycle operations including coordinated creation and deletion
    of Firebase Auth users, UserProfile, and UserStatus documents.
    """

    def __init__(
        self,
        userprofile_ops: UserprofileOperations,
        userstatus_ops: UserstatusOperations,
        userauth_ops: UserauthOperations,
        usersubscription_ops: UsersubscriptionOperations,
        useriam_ops: UserpermissionsOperations,
        catalog_usertype_service: CatalogUserTypeService,
        catalog_subscriptionplan_service: CatalogSubscriptionPlanService,
        logger: Optional[logging.Logger] = None
    ):
        self.userprofile_ops = userprofile_ops
        self.userstatus_ops = userstatus_ops
        self.userauth_ops = userauth_ops
        self.usersubscription_ops = usersubscription_ops
        self.useriam_ops = useriam_ops
        self.catalog_usertype_service = catalog_usertype_service
        self.catalog_subscriptionplan_service = catalog_subscriptionplan_service
        self.logger = logger or logging.getLogger(__name__)






    async def _rollback_user_creation(
        self,
        user_uid: Optional[str],
        profile_created: bool,
        status_created: bool,
        error_context: str
    ) -> None:
        """Rollback user creation on failure."""
        if not user_uid:
            self.logger.error("Rollback cannot proceed: user_uid is None. Context: %s", error_context)
            return

        self.logger.warning("Rolling back user creation for UID: %s. Context: %s", user_uid, error_context)

        # Attempt to clean up Firestore documents if they were created
        if profile_created:
            try:
                await self.userprofile_ops.delete_userprofile(user_uid, "rollback", archive=False)
                self.logger.info("Successfully deleted orphaned UserProfile for: %s", user_uid)
            except Exception as del_prof_e:
                self.logger.error("Failed to delete orphaned UserProfile for %s: %s", user_uid, del_prof_e)
        if status_created:
            try:
                await self.userstatus_ops.delete_userstatus(user_uid, "rollback", archive=False)
                self.logger.info("Successfully deleted orphaned UserStatus for: %s", user_uid)
            except Exception as del_stat_e:
                self.logger.error("Failed to delete orphaned UserStatus for %s: %s", user_uid, del_stat_e)

        # Attempt to delete the orphaned Firebase Auth user
        try:
            await self.userauth_ops.delete_userauth(user_uid)
            self.logger.info("Successfully deleted orphaned Firebase Auth user: %s", user_uid)
        except Exception as delete_e:
            self.logger.error("Failed to delete orphaned Firebase Auth user %s: %s", user_uid, delete_e, exc_info=True)

    def _validate_usertype_consistency(
        self,
        userprofile: UserProfile,
        custom_claims: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Validate usertype consistency between UserProfile and custom claims.

        Args:
            userprofile: UserProfile model to validate
            custom_claims: Custom claims to validate against

        Raises:
            UserCreationError: If usertypes are inconsistent
        """
        if not custom_claims:
            return  # No claims to validate against

        userauth_primary_usertype = custom_claims.get("primary_usertype")
        userauth_secondary_usertypes = custom_claims.get("secondary_usertypes", [])

        # Convert to strings for comparison
        userprofile_primary_str = str(userprofile.primary_usertype)
        userprofile_secondary_strs = [str(ut) for ut in userprofile.secondary_usertypes]

        # Validate primary usertype consistency
        if userauth_primary_usertype and userauth_primary_usertype != userprofile_primary_str:
            raise UserCreationError(
                f"Primary usertype mismatch between UserProfile ({userprofile_primary_str}) "
                f"and custom claims ({userauth_primary_usertype})"
            )

        # Validate secondary usertypes consistency
        if userauth_secondary_usertypes and set(userauth_secondary_usertypes) != set(userprofile_secondary_strs):
            raise UserCreationError(
                f"Secondary usertypes mismatch between UserProfile ({userprofile_secondary_strs}) "
                f"and custom claims ({userauth_secondary_usertypes})"
            )

    # Complete User Creation Methods - New Strategic API

    async def create_user_from_models(
        self,
        userprofile: UserProfile,
        userstatus: UserStatus,
        userauth: Optional[UserAuth] = None,
        custom_claims: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, UserProfile, UserStatus]:
        """
        Create a complete user from ready UserAuth, UserProfile, and UserStatus models.

        This method efficiently commits pre-configured models to database.

        For new user creation (when userauth is provided):
        - Creates Firebase Auth user first to get the actual UID
        - Creates new UserProfile and UserStatus models with the Firebase UID
        - Original models serve as templates

        For existing user (when userauth is None):
        - Models should already have all subscription and permission configuration applied
        - Uses the user_uid from the models to work with existing Firebase Auth user

        Args:
            userprofile: Complete UserProfile model (template for new user, or ready for existing user)
            userstatus: Complete UserStatus model (template for new user, or ready for existing user)
            userauth: Optional UserAuth model. If provided, creates new Firebase Auth user
            custom_claims: Optional custom claims to set (will be merged with userauth.custom_claims)

        Returns:
            Tuple of (user_uid, userprofile, userstatus)
        """
        profile_created = False
        status_created = False
        firebase_user_uid = None

        # Validate that UserProfile and UserStatus have matching user_uid
        if userprofile.user_uid != userstatus.user_uid:
            raise UserCreationError(f"UserProfile and UserStatus user_uid mismatch: {userprofile.user_uid} != {userstatus.user_uid}")

        # Validate usertype consistency between UserProfile and UserAuth if userauth is provided
        try:
            # Step 1: Handle Firebase Auth user creation or validation
            if userauth:
                # Creating new user - Firebase will generate UID
                # Merge custom claims into UserAuth model
                if custom_claims:
                    userauth.custom_claims.update(custom_claims)

                # Validate usertype consistency
                self._validate_usertype_consistency(userprofile, userauth.custom_claims)

                # Create Firebase Auth user with all configuration
                self.logger.info("Creating Firebase Auth user with custom claims for email: %s", userauth.email)
                firebase_user_uid = await self.userauth_ops.create_userauth(userauth)

                # Create new models with the Firebase UID, using original models as templates
                userprofile_data = userprofile.model_dump()
                userprofile_data['user_uid'] = firebase_user_uid
                # Remove id so it gets auto-generated from user_uid
                userprofile_data.pop('id', None)
                final_userprofile = UserProfile(**userprofile_data)

                userstatus_data = userstatus.model_dump()
                userstatus_data['user_uid'] = firebase_user_uid
                # Remove id so it gets auto-generated from user_uid
                userstatus_data.pop('id', None)
                final_userstatus = UserStatus(**userstatus_data)

                user_uid = firebase_user_uid

            else:
                # Working with existing user - use models as-is
                user_uid = userprofile.user_uid
                final_userprofile = userprofile
                final_userstatus = userstatus

                # Validate existing user and apply custom claims if provided
                if not await self.userauth_ops.userauth_exists(user_uid):
                    raise UserCreationError(f"Firebase Auth user {user_uid} does not exist")

                if custom_claims:
                    # Check if custom_claims contain usertype information
                    claims_have_usertype_info = (
                        "primary_usertype" in custom_claims or
                        "secondary_usertypes" in custom_claims
                    )

                    if claims_have_usertype_info:
                        # Validate usertype consistency with provided custom claims
                        self._validate_usertype_consistency(userprofile, custom_claims)
                    else:
                        # Custom claims don't have usertype info, validate against existing auth claims
                        existing_userauth = await self.userauth_ops.get_userauth(user_uid, get_model=True)
                        if existing_userauth and existing_userauth.custom_claims:
                            self._validate_usertype_consistency(userprofile, existing_userauth.custom_claims)

                    await self.userauth_ops.set_userauth_custom_claims(user_uid, custom_claims)
                else:
                    # No custom claims provided - validate against existing userauth custom claims
                    existing_userauth = await self.userauth_ops.get_userauth(user_uid, get_model=True)
                    if existing_userauth and existing_userauth.custom_claims:
                        self._validate_usertype_consistency(userprofile, existing_userauth.custom_claims)

            # Step 2: Create UserProfile and UserStatus in database (2 operations only)
            self.logger.info("Creating UserProfile for user: %s", user_uid)
            await self.userprofile_ops.create_userprofile(final_userprofile)
            profile_created = True

            self.logger.info("Creating UserStatus for user: %s (with %d IAM permissions)",
                           user_uid, len(final_userstatus.iam_permissions))
            await self.userstatus_ops.create_userstatus(final_userstatus)
            status_created = True

            # Step 3: Fetch final state to return
            final_profile = await self.userprofile_ops.get_userprofile(user_uid)
            final_status = await self.userstatus_ops.get_userstatus(user_uid)

            if not final_profile or not final_status:
                raise UserCreationError("Failed to retrieve user documents after creation.")

            self.logger.info("Successfully created user from ready models: %s", user_uid)
            return user_uid, final_profile, final_status

        except Exception as e:
            error_context = f"User creation from models failed: {e}"
            # Use firebase_user_uid if available, otherwise fall back to the original user_uid
            cleanup_uid = firebase_user_uid or userprofile.user_uid
            await self._rollback_user_creation(cleanup_uid, profile_created, status_created, error_context)
            raise UserCreationError(f"Failed to create user from models: {str(e)}") from e

    async def create_user_from_manual_usertype(
        self,
        userprofile: UserProfile,
        usertype: UserType,
        userauth: Optional[UserAuth] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
        user_approval_status: ApprovalStatus = ApprovalStatus.PENDING,
        user_notes: str = "Created with manual usertype configuration",
        extra_insight_credits_override: Optional[int] = None,
        voting_credits_override: Optional[int] = None,
        subscriptionplan_id_override: Optional[str] = None,
        creator_uid: Optional[str] = None
    ) -> Tuple[str, UserProfile, UserStatus]:
        """
        Create a complete user with manual UserType configuration.

        This method builds UserStatus from usertype defaults and applies subscription/permissions
        in memory before committing to database. Organizations are always taken from usertype.

        Args:
            userprofile: Complete UserProfile model (mandatory)
            usertype: Manual UserType configuration (mandatory)
            userauth: Optional UserAuth model. If not provided, assumes user exists
            custom_claims: Optional custom claims to set
            user_approval_status: User approval status (for custom claims)
            user_notes: User notes to set in custom claims
            extra_insight_credits: Override extra credits from usertype
            voting_credits: Override voting credits from usertype
            subscription_plan_id: Override subscription plan from usertype default
            creator_uid: Who is creating this user

        Returns:
            Tuple of (user_uid, userprofile, userstatus)
        """
        try:
            # Always use organizations from usertype
            final_organizations = set(usertype.default_organizations)
            final_extra_credits = extra_insight_credits_override if extra_insight_credits_override is not None else usertype.default_extra_insight_credits
            final_voting_credits = voting_credits_override if voting_credits_override is not None else usertype.default_voting_credits

            # Build initial UserStatus from usertype defaults
            userstatus = UserStatus(
                user_uid=userprofile.user_uid,
                organizations_uids=final_organizations,
                iam_permissions=usertype.granted_iam_permissions or [],
                extra_insight_credits=final_extra_credits,
                voting_credits=final_voting_credits,
                metadata={},
                created_by=creator_uid or f"system_manual_usertype_{userprofile.user_uid}",
                updated_by=creator_uid or f"system_manual_usertype_{userprofile.user_uid}"
            )

            # Apply subscription to UserStatus in memory if plan specified
            plan_to_apply = subscriptionplan_id_override or usertype.default_subscription_plan_if_unpaid
            if plan_to_apply:
                # For now, we'll apply subscription after UserStatus is created
                # Future enhancement: Apply subscription directly to UserStatus in memory
                self.logger.info("Subscription plan %s will be applied after user creation", plan_to_apply)

            # Generate custom claims if not provided
            if not custom_claims:
                custom_claims = {
                    "primary_usertype": str(userprofile.primary_usertype),
                    "secondary_usertypes": [str(ut) for ut in userprofile.secondary_usertypes],
                    "organizations_uids": list(final_organizations),
                    "user_approval_status": str(user_approval_status),
                    "user_notes": user_notes
                }

            # Create user from ready models
            return await self.create_user_from_models(
                userprofile=userprofile,
                userstatus=userstatus,
                userauth=userauth,
                custom_claims=custom_claims
            )

        except Exception as e:
            self.logger.error("Failed to create user from manual usertype: %s", e)
            raise UserCreationError(f"Failed to create user from manual usertype: {str(e)}") from e

    async def create_user_from_catalog_usertype(
        self,
        usertype_id: str,
        userprofile: UserProfile,
        userauth: Optional[UserAuth] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
        user_approval_status: ApprovalStatus = ApprovalStatus.PENDING,
        user_notes: str = "Created from catalog usertype configuration",
        extra_insight_credits_override: Optional[int] = None,
        voting_credits_override: Optional[int] = None,
        subscriptionplan_id_override: Optional[str] = None,
        creator_uid: Optional[str] = None
    ) -> Tuple[str, UserProfile, UserStatus]:
        """
        Create a complete user based on UserType catalog configuration.

        This method fetches UserType from catalog and creates a user with
        appropriate defaults, allowing selective overrides. Organizations are always taken from usertype.

        Args:
            usertype_id: ID of the UserType configuration to fetch from catalog (mandatory)
            userprofile: Complete UserProfile model (mandatory)
            userauth: Optional UserAuth model. If not provided, assumes user exists
            custom_claims: Optional custom claims to set
            user_approval_status: User approval status (for custom claims)
            user_notes: User notes to set in custom claims
            extra_insight_credits: Override extra credits from usertype
            voting_credits: Override voting credits from usertype
            subscriptionplan_id: Override subscription plan from usertype default
            creator_uid: Who is creating this user

        Returns:
            Tuple of (user_uid, userprofile, userstatus)
        """
        try:
            # Step 1: Fetch UserType configuration from catalog
            self.logger.info("Fetching usertype configuration for: %s", usertype_id)
            usertype_config = await self.catalog_usertype_service.get_usertype(usertype_id)
            if not usertype_config:
                raise UserCreationError(f"UserType {usertype_id} not found in catalog")

            # Step 2: Create user using manual usertype method
            return await self.create_user_from_manual_usertype(
                userprofile=userprofile,
                usertype=usertype_config,
                userauth=userauth,
                custom_claims=custom_claims,
                user_approval_status=user_approval_status,
                user_notes=user_notes,
                extra_insight_credits_override=extra_insight_credits_override,
                voting_credits_override=voting_credits_override,
                subscriptionplan_id_override=subscriptionplan_id_override,
                creator_uid=creator_uid
            )

        except Exception as e:
            self.logger.error("Failed to create user from catalog usertype %s: %s", usertype_id, e)
            raise UserCreationError(f"Failed to create user from catalog usertype {usertype_id}: {str(e)}") from e

    # Complete User Deletion

    async def delete_user(
        self,
        user_uid: str,
        delete_auth_user: bool = True,
        delete_profile: bool = True,
        delete_status: bool = True,
        updater_uid: str = "system_deletion",
        archive: bool = True
    ) -> Dict[str, Any]:
        """
        Delete a user holistically, including their auth, profile, and status.

        Args:
            user_uid: The UID of the user to delete.
            delete_auth_user: Whether to delete the Firebase Auth user.
            delete_profile: Whether to delete the UserProfile document.
            delete_status: Whether to delete the UserStatus document.
            updater_uid: The identifier of the entity performing the deletion.
            archive: Whether to archive documents before deletion. Defaults to True.

        Returns:
            A dictionary with the results of the deletion operations.
        """
        results = {
            "auth_deleted_successfully": not delete_auth_user,
            "profile_deleted_successfully": not delete_profile,
            "status_deleted_successfully": not delete_status,
            "errors": []
        }

        # Delete UserProfile
        if delete_profile:
            try:
                results["profile_deleted_successfully"] = await self.userprofile_ops.delete_userprofile(
                    user_uid, updater_uid, archive=archive
                )
            except Exception as e:
                error_msg = f"Failed to delete user profile for {user_uid}: {e}"
                self.logger.error(error_msg, exc_info=True)
                results["errors"].append(error_msg)

        # Delete UserStatus
        if delete_status:
            try:
                results["status_deleted_successfully"] = await self.userstatus_ops.delete_userstatus(
                    user_uid, updater_uid, archive=archive
                )
            except Exception as e:
                error_msg = f"Failed to delete user status for {user_uid}: {e}"
                self.logger.error(error_msg, exc_info=True)
                results["errors"].append(error_msg)

        # Delete Firebase Auth user
        if delete_auth_user:
            try:
                # Assuming delete_userauth also accepts an archive flag for consistency
                results["auth_deleted_successfully"] = await self.userauth_ops.delete_userauth(user_uid, archive=archive)
            except Exception as e:
                error_msg = f"Failed to delete Firebase Auth user {user_uid}: {e}"
                self.logger.error(error_msg, exc_info=True)
                results["errors"].append(error_msg)

        return results

    async def batch_delete_users(
        self,
        user_uids: List[str],
        delete_auth_user: bool,
        delete_profile: bool = True,
        delete_status: bool = True,
        updater_uid: str = "system_batch_deletion",
        archive: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Batch delete multiple users holistically.

        Args:
            user_uids: A list of user UIDs to delete.
            delete_auth_user: Whether to delete the Firebase Auth users.
            delete_profile: Whether to delete the UserProfile documents.
            delete_status: Whether to delete the UserStatus documents.
                updater_uid: The identifier of the entity performing the deletion.
            archive: Overrides the default archival behavior for all users in the batch.

        Returns:
            A dictionary where keys are user UIDs and values are deletion result dictionaries.
        """
        batch_results = {}
        for user_uid in user_uids:
            batch_results[user_uid] = await self.delete_user(
                user_uid=user_uid,
                delete_auth_user=delete_auth_user,
                delete_profile=delete_profile,
                delete_status=delete_status,
                updater_uid=updater_uid,
                archive=archive
            )
        return batch_results

    # Document-level batch operations

    async def batch_delete_user_core_docs(
        self,
        user_uids: List[str],
        updater_uid: str = "system_batch_deletion"
    ) -> Dict[str, Tuple[bool, bool, Optional[str]]]:
        """Batch delete multiple users' documents (profile and status only)"""
        batch_results: Dict[str, Tuple[bool, bool, Optional[str]]] = {}

        # Process sequentially to avoid overwhelming the database
        for user_uid in user_uids:
            self.logger.info("Batch deletion: Processing user_uid: %s", user_uid)
            item_deleted_by = f"{updater_uid}_batch_item_{user_uid}"

            try:
                # Use delete_user but only for documents, not auth
                result = await self.delete_user(
                    user_uid=user_uid,
                    delete_auth_user=False,  # Only delete documents
                    delete_profile=True,
                    delete_status=True,
                    updater_uid=item_deleted_by
                )

                batch_results[user_uid] = (
                    result["profile_deleted_successfully"],
                    result["status_deleted_successfully"],
                    result["errors"][0] if result["errors"] else None
                )
            except Exception as e:
                self.logger.error(f"Batch deletion failed for user {user_uid}: {e}", exc_info=True)
                batch_results[user_uid] = (False, False, str(e))

        return batch_results

    # Utility Methods

    async def user_exists_fully(self, user_uid: str) -> Dict[str, bool]:
        """Check if complete user exists (Auth, Profile, Status)"""
        return {
            "auth_exists": await self.userauth_ops.userauth_exists(user_uid),
            "profile_exists": (await self.userprofile_ops.get_userprofile(user_uid)) is not None,
            "status_exists": (await self.userstatus_ops.get_userstatus(user_uid)) is not None
        }

    async def validate_user_fully_enabled(
        self,
        user_uid: str,
        email_verified_must: bool = True,
        approved_must: bool = True,
        active_subscription_must: bool = True,
        valid_permissions_must: bool = True
    ) -> Dict[str, Any]:
        """
        Validate complete user integrity and operational readiness

        This method performs comprehensive validation to ensure a user is:
        - Complete (auth, profile, status exist)
        - Consistent (matching UIDs and usertypes across components)
        - Enabled (auth enabled, approved status)
        - Operational (active subscription, valid permissions)

        Args:
            user_uid: The UID of the user to validate
            email_verified_must: If True, email must be verified for full enablement (default: True)
            approved_must: If True, approval status must be APPROVED for full enablement (default: True)
            active_subscription_must: If True, active subscription required for full enablement (default: True)
            valid_permissions_must: If True, valid permissions required for full enablement (default: True)

        Returns:
            Dict with validation results including status, errors, and detailed checks
        """
        validation_results = {
            "user_uid": user_uid,
            "exists": {"auth_exists": False, "profile_exists": False, "status_exists": False},
            "is_complete": False,
            "missing_components": [],
            "validation_errors": [],
            "is_fully_enabled": False,
            "detailed_checks": {
                "auth_enabled": False,
                "email_verified": False,
                "approval_status_approved": False,
                "uid_consistency": False,
                "usertype_consistency": False,
                "has_active_subscription": False,
                "has_valid_permissions": False
            }
        }

        try:
            # Get all user components in parallel for efficiency
            userauth_result, userprofile_result, userstatus_result = await asyncio.gather(
                self.userauth_ops.get_userauth(user_uid, get_model=True),
                self.userprofile_ops.get_userprofile(user_uid),
                self.userstatus_ops.get_userstatus(user_uid),
                return_exceptions=True
            )

            # Handle exceptions and determine existence
            validation_results["exists"]["auth_exists"] = not isinstance(userauth_result, Exception) and userauth_result is not None
            validation_results["exists"]["profile_exists"] = not isinstance(userprofile_result, Exception) and userprofile_result is not None
            validation_results["exists"]["status_exists"] = not isinstance(userstatus_result, Exception) and userstatus_result is not None

            validation_results["is_complete"] = all(validation_results["exists"].values())
            validation_results["missing_components"] = [k for k, v in validation_results["exists"].items() if not v]

            # If user is not complete, skip detailed validations
            if not validation_results["is_complete"]:
                validation_results["validation_errors"].append("User is incomplete - missing components")
                return validation_results

            # If we have exceptions instead of models, handle them
            if isinstance(userauth_result, Exception):
                validation_results["validation_errors"].append(f"Auth retrieval error: {str(userauth_result)}")
                return validation_results
            if isinstance(userprofile_result, Exception):
                validation_results["validation_errors"].append(f"Profile retrieval error: {str(userprofile_result)}")
                return validation_results
            if isinstance(userstatus_result, Exception):
                validation_results["validation_errors"].append(f"Status retrieval error: {str(userstatus_result)}")
                return validation_results

            # Additional null checks - should not happen if exists checks passed, but for safety
            if not userauth_result or not userprofile_result or not userstatus_result:
                validation_results["validation_errors"].append("Retrieved user components are null despite existence checks passing")
                return validation_results

            # Type narrow the results to the actual model types after validation
            userauth_record = cast(UserAuth, userauth_result)  # Now known to be UserAuth
            userprofile = cast(UserProfile, userprofile_result)  # Now known to be UserProfile
            userstatus = cast(UserStatus, userstatus_result)  # Now known to be UserStatus

            # Now perform detailed validations with valid models

            # 1. Auth enabled validation (uses the UserAuth model disabled field)
            validation_results["detailed_checks"]["auth_enabled"] = not userauth_record.disabled
            if userauth_record.disabled:
                validation_results["validation_errors"].append("Firebase Auth user is disabled")

            # 2. Email verification validation
            validation_results["detailed_checks"]["email_verified"] = userauth_record.email_verified
            if email_verified_must and not userauth_record.email_verified:
                validation_results["validation_errors"].append("User email is not verified")

            # 3. UID consistency validation
            auth_uid = getattr(userauth_record, 'uid', None) or getattr(userauth_record, 'firebase_uid', None)
            uids_consistent = (
                auth_uid == user_uid and
                userprofile.user_uid == user_uid and
                userstatus.user_uid == user_uid
            )
            validation_results["detailed_checks"]["uid_consistency"] = uids_consistent
            if not uids_consistent:
                validation_results["validation_errors"].append(
                    f"UID inconsistency detected - Auth: {auth_uid}, "
                    f"Profile: {userprofile.user_uid}, Status: {userstatus.user_uid}"
                )

            # 4. Usertype consistency validation
            userauth_claims = userauth_record.custom_claims or {}
            userauth_primary = userauth_claims.get("primary_usertype")
            userauth_secondary = userauth_claims.get("secondary_usertypes", [])

            userprofile_primary_str = str(userprofile.primary_usertype)
            userprofile_secondary_strs = [str(ut) for ut in userprofile.secondary_usertypes]

            usertypes_consistent = (
                userauth_primary == userprofile_primary_str and
                set(userauth_secondary) == set(userprofile_secondary_strs)
            )
            validation_results["detailed_checks"]["usertype_consistency"] = usertypes_consistent
            if not usertypes_consistent:
                validation_results["validation_errors"].append(
                    f"Usertype inconsistency - Auth primary: {userauth_primary}, "
                    f"Profile primary: {userprofile_primary_str}, "
                    f"Auth secondary: {userauth_secondary}, "
                    f"Profile secondary: {userprofile_secondary_strs}"
                )

            # 5. Approval status validation
            user_approval_status = userauth_claims.get("user_approval_status")
            approval_approved = user_approval_status == "APPROVED"
            validation_results["detailed_checks"]["approval_status_approved"] = approval_approved
            if approved_must and not approval_approved:
                validation_results["validation_errors"].append(
                    f"User approval status is not APPROVED (current: {user_approval_status})"
                )

            # 6. Active subscription validation - use UserStatus methods
            has_active_subscription = userstatus.is_subscription_active()
            validation_results["detailed_checks"]["has_active_subscription"] = has_active_subscription
            if active_subscription_must and not has_active_subscription:
                validation_results["validation_errors"].append("User has no active subscription")

            # 7. Valid permissions validation - use UserStatus get_valid_permissions method
            valid_permissions = userstatus.get_valid_permissions()
            has_valid_permissions = len(valid_permissions) > 0

            validation_results["detailed_checks"]["has_valid_permissions"] = has_valid_permissions
            if valid_permissions_must and not has_valid_permissions:
                validation_results["validation_errors"].append("User has no valid (non-expired) IAM permissions")

            # Overall validation result - only consider checks that are required based on flags
            required_checks = []
            required_checks.append(validation_results["detailed_checks"]["auth_enabled"])  # Always required
            required_checks.append(validation_results["detailed_checks"]["uid_consistency"])  # Always required
            required_checks.append(validation_results["detailed_checks"]["usertype_consistency"])  # Always required

            if email_verified_must:
                required_checks.append(validation_results["detailed_checks"]["email_verified"])
            if approved_must:
                required_checks.append(validation_results["detailed_checks"]["approval_status_approved"])
            if active_subscription_must:
                required_checks.append(validation_results["detailed_checks"]["has_active_subscription"])
            if valid_permissions_must:
                required_checks.append(validation_results["detailed_checks"]["has_valid_permissions"])

            validation_results["is_fully_enabled"] = all(required_checks)

        except Exception as e:
            validation_results["validation_errors"].append(f"Validation process error: {str(e)}")

        return validation_results
