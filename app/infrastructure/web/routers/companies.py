"""
Companies router for admin operations.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database.connection import get_database_session
from ....application.use_cases.admin.manage_companies import ManageCompaniesUseCase
from ....infrastructure.database.repositories.company_repository_impl import CompanyRepositoryImpl
from ..schemas.company_schema import CompanyCreateSchema, CompanyUpdateSchema, CompanyResponseSchema
from ....core.exceptions import EntityNotFoundException, EntityAlreadyExistsException

router = APIRouter(prefix="/companies")


@router.get("/public", response_model=List[CompanyResponseSchema])
async def get_public_companies(
        active_only: bool = True,
        session: AsyncSession = Depends(get_database_session)
):
    """Get all companies (public endpoint)."""
    try:
        # For now, return mock data to test the frontend
        from datetime import datetime
        
        mock_companies = [
            CompanyResponseSchema(
                id="1",
                name="TransAndina",
                email="info@transandina.com",
                phone="+51 999 888 777",
                address="Av. Javier Prado 123, Lima",
                description="Empresa líder en transporte interprovincial",
                status="active",
                rating=4.5,
                total_trips=500,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            CompanyResponseSchema(
                id="2",
                name="Cruz del Sur",
                email="info@cruzdelsur.com",
                phone="+51 999 777 666",
                address="Av. Grau 456, Lima",
                description="Transporte de lujo y confort",
                status="active",
                rating=4.8,
                total_trips=750,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            CompanyResponseSchema(
                id="3",
                name="Oltursa",
                email="info@oltursa.com",
                phone="+51 999 666 555",
                address="Av. Túpac Amaru 789, Lima",
                description="Transporte económico y confiable",
                status="active",
                rating=4.2,
                total_trips=300,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        return mock_companies

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve companies"
        )

def require_admin(request: Request):
    """Require admin role."""
    if not hasattr(request.state, 'user') or request.state.user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

@router.get("/", response_model=List[CompanyResponseSchema])
async def get_companies(
        request: Request,
        active_only: bool = True,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Get all companies."""
    try:
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageCompaniesUseCase(company_repository)

        companies = await manage_use_case.get_companies(active_only=active_only)
        return companies

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve companies"
        )

@router.post("/", response_model=CompanyResponseSchema)
async def create_company(
        company_data: CompanyCreateSchema,
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Create a new company."""
    try:
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageCompaniesUseCase(company_repository)

        result = await manage_use_case.create_company(
            name=company_data.name,
            email=company_data.email,
            phone=company_data.phone,
            address=company_data.address,
            description=company_data.description
        )

        return result

    except EntityAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Company creation failed"
        )


@router.put("/{company_id}", response_model=CompanyResponseSchema)
async def update_company(
        company_id: str,
        company_data: CompanyUpdateSchema,
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Update a company."""
    try:
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageCompaniesUseCase(company_repository)

        result = await manage_use_case.update_company(
            company_id=company_id,
            name=company_data.name,
            phone=company_data.phone,
            address=company_data.address,
            description=company_data.description
        )

        return result

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Company update failed"
        )


@router.delete("/{company_id}")
async def delete_company(
        company_id: str,
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Delete a company."""
    try:
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageCompaniesUseCase(company_repository)

        success = await manage_use_case.delete_company(company_id)

        if success:
            return {"message": "Company deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Company deletion failed"
        )