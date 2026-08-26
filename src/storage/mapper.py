from .models import Trait, TraitImplementor, TraitMethod

def trait_to_dataclasses(data: dict):

    trait = Trait(
        id=None,
        name=data["title"],
        type=data["type"],
        declaration=data.get("declaration"),
        description=data.get("description"),
        source_text=data.get("source", {}).get("text"),
        source_href=data.get("source", {}).get("href"),
    )

    methods = [
        TraitMethod(
            id=None,
            trait_id=0,  # assigned after SQLite inserts Trait
            name=method["name"],
            kind=method["kind"],
            href=method.get("href"),
            signature=method.get("signature"),
            description=method.get("description"),
            source_text=method.get("source", {}).get("text"),
            source_href=method.get("source", {}).get("href"),
        )
        for method in data.get("methods", [])
    ]

    implementors = [
        TraitImplementor(
            id=None,
            trait_id=0,  # assigned after SQLite inserts Trait
            name=implementor["name"],
            href=implementor.get("href"),
            source_text=implementor.get("source", {}).get("text"),
            source_href=implementor.get("source", {}).get("href"),
        )
        for implementor in data.get("implementors", [])
    ]

    return trait, methods, implementors