from flask import jsonify
from sqlalchemy.orm.session import Session

from balance_api.api import Resource
from balance_api.connection.db import database_operation
from balance_api.models.assets import (
    Asset,
    search_assets as search_a,
)


class AssetResource(Resource):
    fields = [
        "isin",
        "description",
        "currency",
        "price",
    ]

    protected_fields = [
        "created_at",
        "updated_at",
    ]

    def serialize(self, **kwargs) -> dict:
        resource = super().serialize()
        asset: Asset = self.instance

        resource.update(
            {
                "isin": asset.isin,
                "description": asset.description,
                "currency": asset.currency,
                "price": asset.price,
            }
        )

        resource.update(**kwargs)

        return resource

    @classmethod
    def deserialize(cls, asset_data: dict, create=True) -> dict:
        asset_resource = {}

        for field in cls.fields:
            asset_resource[field] = asset_data.get(field, None)
        for field in cls.protected_fields:
            asset_resource.pop(field, None)

        return asset_resource


@database_operation(max_tries=3)
def search_assets(keywords: str, session: Session):
    assets = search_a(keywords, session)
    return jsonify(
        {
            "assets": [AssetResource(asset).serialize() for asset in assets],
        }
    )
