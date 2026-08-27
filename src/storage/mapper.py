from .models import Trait, TraitImplementor, TraitMethod

def trait_to_dataclasses(data: dict):

    trait = Trait(
        id=None,
        name=data["title"],
        type=data["type"],
        declaration=data.get("declaration"),
        description=data.get("description"),
        source_text="|".join([i.get("text") for i in data.get("source", {})]),
        source_href="|".join([i.get("href") for i in data.get("source", {})])
    )

    methods = [
        TraitMethod(
            id=None,
            trait_id=0,  # assigned after SQLite inserts Trait
            name=method["name"],
            kind="required",
            href=method.get("href"),
            signature=method.get("signature"),
            description=method.get("description"),
            source_text="|".join([i.get("text") for i in data.get("source", {})]),
            source_href="|".join([i.get("href") for i in data.get("source", {})])
        )
        for method in data.get("required_methods", [])
    ] + [
        TraitMethod(
            id=None,
            trait_id=0,  # assigned after SQLite inserts Trait
            name=method["name"],
            kind="provided",
            href=method.get("href"),
            signature=method.get("signature"),
            description=method.get("description"),
            source_text="|".join([i.get("text") for i in data.get("source", {})]),
            source_href="|".join([i.get("href") for i in data.get("source", {})])
        )
        for method in data.get("provided_methods", [])
    ]

    implementors = [
        TraitImplementor(
            id=None,
            trait_id=0,  # assigned after SQLite inserts Trait
            name=implementor["name"],
            href=implementor.get("href"),
            source_text="|".join([i.get("text") for i in data.get("source", {})]),
            source_href="|".join([i.get("href") for i in data.get("source", {})])

        )
        for implementor in data.get("implementors", [])
    ]

    return trait, methods, implementors