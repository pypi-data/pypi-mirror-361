from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RetriverRequest")


@_attrs_define
class RetriverRequest:
    """
    Attributes:
        api_key (str):
        query (str): Query to search for
        base_url (Union[Unset, str]): Elasticsearch URL Default: 'http://localhost:9200'.
        index_name (Union[Unset, str]): Elasticsearch index name Default: 'default'.
        embedding_model (Union[Unset, str]):  Default: 'sentence-transformers/all-MiniLM-L6-v2'.
    """

    api_key: str
    query: str
    base_url: Union[Unset, str] = "http://localhost:9200"
    index_name: Union[Unset, str] = "default"
    embedding_model: Union[Unset, str] = "sentence-transformers/all-MiniLM-L6-v2"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        api_key = self.api_key

        query = self.query

        base_url = self.base_url

        index_name = self.index_name

        embedding_model = self.embedding_model

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "api_key": api_key,
                "query": query,
            }
        )
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if index_name is not UNSET:
            field_dict["index_name"] = index_name
        if embedding_model is not UNSET:
            field_dict["embedding_model"] = embedding_model

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        api_key = d.pop("api_key")

        query = d.pop("query")

        base_url = d.pop("base_url", UNSET)

        index_name = d.pop("index_name", UNSET)

        embedding_model = d.pop("embedding_model", UNSET)

        retriver_request = cls(
            api_key=api_key,
            query=query,
            base_url=base_url,
            index_name=index_name,
            embedding_model=embedding_model,
        )

        retriver_request.additional_properties = d
        return retriver_request

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
