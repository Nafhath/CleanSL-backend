from fastapi import APIRouter
from app.models.schemas import AddressCreate, AddressUpdate
from app.services.addresses import list_addresses, get_address, create_address, update_address, delete_address

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get("")
def read_addresses():
    return list_addresses()


@router.get("/{address_id}")
def read_address(address_id: str):
    return get_address(address_id)


@router.post("")
def add_address(payload: AddressCreate):
    return create_address(payload.model_dump(exclude_none=True))


@router.put("/{address_id}")
def edit_address(address_id: str, payload: AddressUpdate):
    return update_address(address_id, payload.model_dump(exclude_none=True))


@router.delete("/{address_id}")
def remove_address(address_id: str):
    return delete_address(address_id)