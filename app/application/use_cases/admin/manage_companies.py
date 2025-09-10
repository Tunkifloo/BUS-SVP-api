"""
Manage companies use case.
"""
from typing import List, Dict, Any, Optional
from app.domain.entities.company import Company
from app.domain.repositories.company_repository import CompanyRepository
from app.domain.value_objects.email import Email
from app.core.exceptions import EntityNotFoundException, EntityAlreadyExistsException
from app.shared.decorators import log_execution


class ManageCompaniesUseCase:
    """Use case for managing companies."""

    def __init__(self, company_repository: CompanyRepository):
        self._company_repository = company_repository

    @log_execution(log_duration=True)
    async def create_company(
            self,
            name: str,
            email: str,
            phone: str,
            address: Optional[str] = None,
            description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new company.

        Args:
            name: Company name
            email: Company email
            phone: Company phone
            address: Company address (optional)
            description: Company description (optional)

        Returns:
            Created company information

        Raises:
            EntityAlreadyExistsException: If email already exists
        """
        # Check if email already exists
        email_obj = Email(email)
        existing_company = await self._company_repository.find_by_email(email_obj)

        if existing_company:
            raise EntityAlreadyExistsException("Company", email)

        # Check if name already exists
        existing_by_name = await self._company_repository.find_by_name(name)
        if existing_by_name:
            raise EntityAlreadyExistsException("Company", name)

        # Create company entity
        company = Company(
            name=name,
            email=email,
            phone=phone,
            address=address,
            description=description
        )

        # Save company
        saved_company = await self._company_repository.save(company)

        return {
            "id": saved_company.id,
            "name": saved_company.name,
            "email": saved_company.email.value,
            "phone": saved_company.phone,
            "address": saved_company.address,
            "description": saved_company.description,
            "status": saved_company.status.value,
            "rating": saved_company.rating,
            "created_at": saved_company.created_at.isoformat()
        }

    @log_execution(log_duration=True)
    async def update_company(
            self,
            company_id: str,
            name: Optional[str] = None,
            phone: Optional[str] = None,
            address: Optional[str] = None,
            description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update company information.

        Args:
            company_id: Company ID
            name: New name (optional)
            phone: New phone (optional)
            address: New address (optional)
            description: New description (optional)

        Returns:
            Updated company information

        Raises:
            EntityNotFoundException: If company doesn't exist
        """
        # Find company
        company = await self._company_repository.find_by_id(company_id)
        if not company:
            raise EntityNotFoundException("Company", company_id)

        # Update basic info
        company.update_basic_info(
            name=name,
            phone=phone,
            address=address,
            description=description
        )

        # Save updated company
        updated_company = await self._company_repository.update(company)

        return {
            "id": updated_company.id,
            "name": updated_company.name,
            "email": updated_company.email.value,
            "phone": updated_company.phone,
            "address": updated_company.address,
            "description": updated_company.description,
            "status": updated_company.status.value,
            "rating": updated_company.rating,
            "updated_at": updated_company.updated_at.isoformat()
        }

    @log_execution(log_duration=True)
    async def get_companies(
            self,
            active_only: bool = False,
            limit: int = 100,
            offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get list of companies.

        Args:
            active_only: Only return active companies
            limit: Limit results
            offset: Offset for pagination

        Returns:
            List of companies
        """
        if active_only:
            companies = await self._company_repository.find_active(limit=limit, offset=offset)
        else:
            companies = await self._company_repository.find_all(limit=limit, offset=offset)

        return [
            {
                "id": company.id,
                "name": company.name,
                "email": company.email.value,
                "phone": company.phone,
                "address": company.address,
                "description": company.description,
                "status": company.status.value,
                "rating": company.rating,
                "total_trips": company.total_trips,
                "created_at": company.created_at.isoformat()
            }
            for company in companies
        ]

    @log_execution(log_duration=True)
    async def delete_company(self, company_id: str) -> bool:
        """
        Delete a company.

        Args:
            company_id: Company ID

        Returns:
            True if deletion was successful

        Raises:
            EntityNotFoundException: If company doesn't exist
        """
        # Find company
        company = await self._company_repository.find_by_id(company_id)
        if not company:
            raise EntityNotFoundException("Company", company_id)

        # Soft delete
        company.mark_as_deleted()
        await self._company_repository.update(company)

        return True