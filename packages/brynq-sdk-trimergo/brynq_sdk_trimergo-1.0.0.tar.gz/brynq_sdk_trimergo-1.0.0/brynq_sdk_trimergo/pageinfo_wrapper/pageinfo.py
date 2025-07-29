"""Defines PageInfo, Criterion, and Sorter classes for Trimergo API interactions. It wraps/mirrors pageinof.js, which handles query parameters for the trimergo api.

These classes are used to construct and encode query parameters for filtering,
sorting, and paginating Trimergo API responses, particularly for services
like Timesheet.
"""

import base64
import json
from typing import Any, Dict, List, Optional

#  Helpers – JS‑identical Base64‑URL codec
_B64_PLUS = b"+"
_B64_SLASH = b"/"
_B64_DASH = b"-"
_B64_UNDERSCORE = b"_"
_B64_PAD = b"="

def _b64url_encode(raw: str) -> str:
    """Encodes a string to a URL-safe Base64 string."""
    out = base64.b64encode(raw.encode())
    out = out.replace(_B64_PLUS, _B64_DASH).replace(_B64_SLASH, _B64_UNDERSCORE)
    return out.rstrip(_B64_PAD).decode()

def _b64url_decode(data: str) -> str:
    """Decodes a URL-safe Base64 string."""
    fixed = data.replace("-", "+").replace("_", "/")
    fixed += "=" * (-len(fixed) % 4)
    return base64.b64decode(fixed).decode()

class Criterion:
    """Represents a filter criterion for Trimergo API queries."""
    __slots__ = ("f", "o", "v", "q")

    def __init__(self,
                 field: str,
                 operator: str,
                 value: Any,
                 sub: "Optional[Criterion]" = None):
        """Initializes a Criterion.

        Args:
            field (str): The field to filter on.
            operator (str): The operator to use (e.g., '=', '>', 'LIKE').
            value (Any): The value to compare against.
            sub (Optional[Criterion]): A sub-criterion for nested queries.
        """
        self.f: str = field
        self.o: str = operator
        self.v: Any = value
        self.q: List[Dict[str, Any]] = []
        if sub is not None:
            self.q.append(sub.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """Converts the criterion to its dictionary representation."""
        return {"f": self.f,
                "o": self.o,
                "v": self.v,
                "q": self.q}

class Sorter:
    """Represents a sort order for Trimergo API queries."""
    ASC = "asc"
    DESC = "desc"
    __slots__ = ("f", "t")

    def __init__(self, field: str,
                 direction: str):
        """Initializes a Sorter.

        Args:
            field (str): The field to sort by.
            direction (str): The sort direction ('asc' or 'desc').

        Raises:
            ValueError: If direction is not 'asc' or 'desc'.
        """
        if (d := direction.lower()) not in (self.ASC, self.DESC):
            raise ValueError("Sorter direction must be 'asc' or 'desc'.")
        self.f: str = field
        self.t: str = d

    def to_dict(self) -> Dict[str, Any]:
        """Converts the sorter to its dictionary representation."""
        return {"f": self.f, "t": self.t}

class PageInfo:
    """Represents pagination, filtering, and sorting parameters for Trimergo API queries.

    This class provides methods to add criteria and sorters, and to encode these
    parameters into the format expected by the Trimergo API.
    """
    def __init__(self) -> None:
        """Initializes a PageInfo object with default pagination settings."""
        self.pageNo: int = 1
        self.rpp: int = 1000  # Records Per Page
        self.criteria: List[Dict[str, Any]] = []
        self.haystack: Dict[str, Any] = {"fields": [], "needle": ""}
        self.sorters: List[Dict[str, Any]] = []

    def addCriterion(self, c: Criterion) -> None:
        """Adds a criterion to the PageInfo.

        Args:
            c (Criterion): The criterion to add.
        """
        self.criteria.append({"q": c.to_dict()})

    def wrapCriterion(self, wrapper: Criterion) -> None:
        """Wraps existing criteria with a new (outer) criterion, typically for AND logic.

        Args:
            wrapper (Criterion): The criterion to wrap existing criteria with.
        """
        for item in self.criteria:
            wrapper.q.append(item["q"])
        self.criteria = [{"q": wrapper.to_dict()}]

    def addSorter(self, s: Sorter) -> None:
        """Adds a sorter to the PageInfo.

        Args:
            s (Sorter): The sorter to add.
        """
        self.sorters.append({"s": s.to_dict()})

    def _criteria_json(self) -> str:
        """Internal helper to get criteria as a JSON string."""
        # Trimergo's API expects empty sub-queries 'q':[] to be omitted
        return json.dumps(self.criteria).replace(',"q":[]', "")

    def getQ(self) -> str:
        """Gets the Base64-URL encoded criteria string ('q' parameter)."""
        return _b64url_encode(self._criteria_json()) if self.criteria else ""

    def getH(self) -> str:
        """Gets the Base64-URL encoded haystack search string ('h' parameter)."""
        if not (self.haystack["fields"] and self.haystack["needle"]):
            return ""
        # Assuming haystack structure is correct for direct dump
        return _b64url_encode(json.dumps({"h": self.haystack}))

    def getO(self) -> str:
        """Gets the Base64-URL encoded sorters string ('o' parameter)."""
        return _b64url_encode(json.dumps(self.sorters)) if self.sorters else ""

    def getProperties(self) -> Dict[str, str]:
        """Constructs a dictionary of all page info properties for API query parameters."""
        props: Dict[str, str] = {
            "pageNo": str(self.pageNo),
            "rpp": str(self.rpp)
        }
        if q_param := self.getQ():
            props["q"] = q_param
        if h_param := self.getH():
            props["h"] = h_param
        if o_param := self.getO():
            props["o"] = o_param
        return props
