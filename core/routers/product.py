from http import HTTPStatus
from typing import Iterable

from beanie.odm.fields import PydanticObjectId
from fastapi import APIRouter, HTTPException

from core.models import Product
from core.settings import settings

router = APIRouter(tags=['Products'])


@router.get('/')
async def list_products() -> Iterable[Product]:
    return await Product.find().to_list()


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_product(product: Product) -> Product:
    await product.insert()

    return product


@router.get('/{id}/')
async def retrieve_product(id: PydanticObjectId) -> Product:
    if (product := await Product.find_one(Product.id == id)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Product not found.')

    return product


@router.delete('/{id}/', status_code=204)
async def delete_product(id: PydanticObjectId):
    if (product := await Product.find_one(Product.id == id)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Product not found.')

    await product.delete()
