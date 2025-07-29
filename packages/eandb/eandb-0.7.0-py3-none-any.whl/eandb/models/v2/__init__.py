import enum
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ErrorType(enum.Enum):
    INVALID_BARCODE = enum.auto()
    PRODUCT_NOT_FOUND = enum.auto()
    INVALID_JWT = enum.auto()
    ACCOUNT_NOT_CONFIRMED = enum.auto()
    JWT_REVOKED = enum.auto()
    JWT_EXPIRED = enum.auto()
    EMPTY_BALANCE = enum.auto()


_ERROR_MESSAGE_TO_CODE = {
    'Product not found: ': ErrorType.PRODUCT_NOT_FOUND,
    'JWT is missing or invalid, check Authorization header': ErrorType.INVALID_JWT,
    'Your account is not confirmed': ErrorType.ACCOUNT_NOT_CONFIRMED,
    'JWT revoked': ErrorType.JWT_REVOKED,
    'JWT expired': ErrorType.JWT_EXPIRED,
    'Your account balance is empty': ErrorType.EMPTY_BALANCE
}


class Error(BaseModel):
    code: int
    description: str


class EandbResponse(BaseModel):
    error: Optional[Error] = None

    def get_error_type(self) -> Optional[ErrorType]:
        if not self.error:
            return None

        if self.error.code == 400:
            return ErrorType.INVALID_BARCODE

        for msg, code in _ERROR_MESSAGE_TO_CODE.items():
            if self.error.description.startswith(msg):
                return code

        return None


class Amount(BaseModel):
    class AmountValue(BaseModel):
        value: Decimal
        unit: str

    equals: Optional[AmountValue] = None
    greaterThan: Optional[AmountValue] = None
    lessThan: Optional[AmountValue] = None


class DimensionsType(BaseModel):
    width: Optional[Amount] = None
    height: Optional[Amount] = None
    length: Optional[Amount] = None
    depth: Optional[Amount] = None


class Product(BaseModel):
    class BarcodeDetails(BaseModel):
        type: str
        description: str
        country: Optional[str] = None

    class Category(BaseModel):
        id: str
        titles: dict[str, str]

    class Manufacturer(BaseModel):
        id: Optional[str] = None
        titles: dict[str, str]
        wikidataId: Optional[str] = None

    class Image(BaseModel):
        url: str
        isCatalog: bool
        width: int
        height: int

    class Metadata(BaseModel):
        class ExternalIds(BaseModel):
            amazonAsin: Optional[str]

        class Generic(BaseModel):
            class Color(BaseModel):
                baseColor: str
                shade: Optional[str] = None

            class Contributor(BaseModel):
                names: dict[str, str]
                type: str

            class Dimensions(BaseModel):
                product: Optional[DimensionsType] = None
                packaging: Optional[DimensionsType] = None

            class Ingredients(BaseModel):
                class Ingredient(BaseModel):
                    originalNames: Optional[dict[str, str]] = None
                    id: Optional[str] = None
                    canonicalNames: Optional[dict[str, str]] = None
                    properties: Optional[dict[str, list[str]]] = None
                    amount: Optional[Amount] = None
                    isVegan: Optional[bool] = None
                    isVegetarian: Optional[bool] = None
                    subIngredients: Optional[list['Product.Metadata.Generic.Ingredients.Ingredient']] = None

                groupName: Optional[str]
                ingredientsGroup: list[Ingredient]

            class Weight(BaseModel):
                net: Optional[Amount] = None
                gross: Optional[Amount] = None
                unknown: Optional[Amount] = None

            ageGroups: Optional[list[str]] = None
            colors: Optional[list[Color]] = None
            contributors: Optional[list[Contributor]] = None
            dimensions: Optional[Dimensions] = None
            ingredients: Optional[list[Ingredients]] = None
            manufacturerCode: Optional[str] = None
            power: Optional[Amount] = None
            volume: Optional[Amount] = None
            weight: Optional[Weight] = None

        class Food(BaseModel):
            class Nutriments(BaseModel):
                energy: Optional[Amount] = None
                fat: Optional[Amount] = None
                saturatedFat: Optional[Amount] = None
                transFat: Optional[Amount] = None
                proteins: Optional[Amount] = None
                carbohydrates: Optional[Amount] = None
                fiber: Optional[Amount] = None
                totalSugars: Optional[Amount] = None
                addedSugars: Optional[Amount] = None
                cholesterol: Optional[Amount] = None
                sodium: Optional[Amount] = None
                potassium: Optional[Amount] = None
                calcium: Optional[Amount] = None
                iron: Optional[Amount] = None
                vitaminD: Optional[Amount] = None

            nutrimentsPer100Grams: Optional[Nutriments]

        class PrintBook(BaseModel):
            numPages: Optional[int] = None
            bisacCodes: Optional[list[str]] = None
            bindingType: Optional[str] = None

        class MusicCD(BaseModel):
            numberOfDiscs: Optional[int] = None

        class Media(BaseModel):
            publicationYear: Optional[int] = None

        externalIds: Optional[ExternalIds] = None
        generic: Optional[Generic] = None
        food: Optional[Food] = None
        printBook: Optional[PrintBook] = None
        musicCD: Optional[MusicCD] = None
        media: Optional[Media] = None

    barcode: str
    barcodeDetails: BarcodeDetails
    titles: dict[str, str]
    categories: list[Category]
    manufacturer: Optional[Manufacturer]
    relatedBrands: list[Manufacturer]
    images: list[Image]
    metadata: Optional[Metadata]


class ProductResponse(EandbResponse):
    balance: int
    product: Product
