from models import Trait, TraitImplementor, TraitMethod

def trait_to_dataclasses(data: dict):

    trait = Trait(
        id=None,
        name=data["name"],
        type=data["type"],
        declaration=data.get("declaration"),
        description=data.get("description"),
        source_href=data.get("source_href"),
        source_line=data.get("source_line"),
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
            source_href=method.get("source_href"),
            source_line=method.get("source_line"),
        )
        for method in data.get("methods", [])
    ]

    implementors = [
        TraitImplementor(
            id=None,
            trait_id=0,  # assigned after SQLite inserts Trait
            name=implementor["name"],
            href=implementor.get("href"),
            source_href=implementor.get("source_href"),
            source_line=implementor.get("source_line"),
        )
        for implementor in data.get("implementors", [])
    ]

    return trait, methods, implementors