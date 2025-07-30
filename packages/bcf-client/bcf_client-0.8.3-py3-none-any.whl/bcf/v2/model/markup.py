import sys
from dataclasses import dataclass, field
from typing import Optional

from xsdata.models.datatype import XmlDateTime

DATACLASS_KWARGS = {} if sys.version_info < (3, 10) else {"slots": True, "kw_only": True}


@dataclass(**DATACLASS_KWARGS)
class BimSnippet:
    reference: str = field(
        metadata={
            "name": "Reference",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    reference_schema: str = field(
        metadata={
            "name": "ReferenceSchema",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    snippet_type: str = field(
        metadata={
            "name": "SnippetType",
            "type": "Attribute",
            "required": True,
        }
    )
    is_external: bool = field(
        default=False,
        metadata={
            "name": "isExternal",
            "type": "Attribute",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class CommentViewpoint:
    class Meta:
        global_type = False

    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
        }
    )


@dataclass(**DATACLASS_KWARGS)
class HeaderFile:
    class Meta:
        global_type = False

    filename: Optional[str] = field(
        default=None,
        metadata={
            "name": "Filename",
            "type": "Element",
            "namespace": "",
        },
    )
    date: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "Date",
            "type": "Element",
            "namespace": "",
        },
    )
    reference: Optional[str] = field(
        default=None,
        metadata={
            "name": "Reference",
            "type": "Element",
            "namespace": "",
        },
    )
    ifc_project: Optional[str] = field(
        default=None,
        metadata={
            "name": "IfcProject",
            "type": "Attribute",
            "length": 22,
            "pattern": r"[0-9,A-Z,a-z,_$]*",
        },
    )
    ifc_spatial_structure_element: Optional[str] = field(
        default=None,
        metadata={
            "name": "IfcSpatialStructureElement",
            "type": "Attribute",
            "length": 22,
            "pattern": r"[0-9,A-Z,a-z,_$]*",
        },
    )
    is_external: bool = field(
        default=True,
        metadata={
            "name": "isExternal",
            "type": "Attribute",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class TopicDocumentReference:
    class Meta:
        global_type = False

    referenced_document: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReferencedDocument",
            "type": "Element",
            "namespace": "",
        },
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "",
        },
    )
    guid: Optional[str] = field(
        default=None,
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
        },
    )
    is_external: bool = field(
        default=False,
        metadata={
            "name": "isExternal",
            "type": "Attribute",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class TopicRelatedTopic:
    class Meta:
        global_type = False

    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
        }
    )


@dataclass(**DATACLASS_KWARGS)
class ViewPoint:
    viewpoint: Optional[str] = field(
        default=None,
        metadata={
            "name": "Viewpoint",
            "type": "Element",
            "namespace": "",
        },
    )
    snapshot: Optional[str] = field(
        default=None,
        metadata={
            "name": "Snapshot",
            "type": "Element",
            "namespace": "",
        },
    )
    index: Optional[int] = field(
        default=None,
        metadata={
            "name": "Index",
            "type": "Element",
            "namespace": "",
        },
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
        }
    )


@dataclass(**DATACLASS_KWARGS)
class Comment:
    date: XmlDateTime = field(
        metadata={
            "name": "Date",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    author: str = field(
        metadata={
            "name": "Author",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    comment: str = field(
        metadata={
            "name": "Comment",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    viewpoint: Optional[CommentViewpoint] = field(
        default=None,
        metadata={
            "name": "Viewpoint",
            "type": "Element",
            "namespace": "",
        },
    )
    modified_date: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "ModifiedDate",
            "type": "Element",
            "namespace": "",
        },
    )
    modified_author: Optional[str] = field(
        default=None,
        metadata={
            "name": "ModifiedAuthor",
            "type": "Element",
            "namespace": "",
        },
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
        }
    )


@dataclass(**DATACLASS_KWARGS)
class Header:
    file: list[HeaderFile] = field(
        default_factory=list,
        metadata={
            "name": "File",
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        },
    )


@dataclass(**DATACLASS_KWARGS)
class Topic:
    reference_link: list[str] = field(
        default_factory=list,
        metadata={
            "name": "ReferenceLink",
            "type": "Element",
            "namespace": "",
        },
    )
    title: str = field(
        metadata={
            "name": "Title",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    priority: Optional[str] = field(
        default=None,
        metadata={
            "name": "Priority",
            "type": "Element",
            "namespace": "",
        },
    )
    index: Optional[int] = field(
        default=None,
        metadata={
            "name": "Index",
            "type": "Element",
            "namespace": "",
        },
    )
    labels: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Labels",
            "type": "Element",
            "namespace": "",
        },
    )
    creation_date: XmlDateTime = field(
        metadata={
            "name": "CreationDate",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    creation_author: str = field(
        metadata={
            "name": "CreationAuthor",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    modified_date: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "ModifiedDate",
            "type": "Element",
            "namespace": "",
        },
    )
    modified_author: Optional[str] = field(
        default=None,
        metadata={
            "name": "ModifiedAuthor",
            "type": "Element",
            "namespace": "",
        },
    )
    due_date: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "DueDate",
            "type": "Element",
            "namespace": "",
        },
    )
    assigned_to: Optional[str] = field(
        default=None,
        metadata={
            "name": "AssignedTo",
            "type": "Element",
            "namespace": "",
        },
    )
    stage: Optional[str] = field(
        default=None,
        metadata={
            "name": "Stage",
            "type": "Element",
            "namespace": "",
        },
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "",
        },
    )
    bim_snippet: Optional[BimSnippet] = field(
        default=None,
        metadata={
            "name": "BimSnippet",
            "type": "Element",
            "namespace": "",
        },
    )
    document_reference: list[TopicDocumentReference] = field(
        default_factory=list,
        metadata={
            "name": "DocumentReference",
            "type": "Element",
            "namespace": "",
        },
    )
    related_topic: list[TopicRelatedTopic] = field(
        default_factory=list,
        metadata={
            "name": "RelatedTopic",
            "type": "Element",
            "namespace": "",
        },
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
        }
    )
    topic_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "TopicType",
            "type": "Attribute",
        },
    )
    topic_status: Optional[str] = field(
        default=None,
        metadata={
            "name": "TopicStatus",
            "type": "Attribute",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class Markup:
    header: Optional[Header] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
            "namespace": "",
        },
    )
    topic: Topic = field(
        metadata={
            "name": "Topic",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    comment: list[Comment] = field(
        default_factory=list,
        metadata={
            "name": "Comment",
            "type": "Element",
            "namespace": "",
        },
    )
    viewpoints: list[ViewPoint] = field(
        default_factory=list,
        metadata={
            "name": "Viewpoints",
            "type": "Element",
            "namespace": "",
        },
    )
