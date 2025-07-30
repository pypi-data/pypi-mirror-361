# danistay_mcp_module/models.py

from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import List, Optional, Dict, Any

class DanistayBaseSearchRequest(BaseModel):
    """Base model for common search parameters for Danistay."""
    pageSize: int = Field(default=10, ge=1, le=10)
    pageNumber: int = Field(default=1, ge=1)
    # siralama and siralamaDirection are part of detailed search, not necessarily keyword search
    # as per user's provided payloads.

class DanistayKeywordSearchRequestData(BaseModel):
    """Internal data model for the keyword search payload's 'data' field."""
    andKelimeler: List[str] = Field(default_factory=list)
    orKelimeler: List[str] = Field(default_factory=list)
    notAndKelimeler: List[str] = Field(default_factory=list)
    notOrKelimeler: List[str] = Field(default_factory=list)
    pageSize: int
    pageNumber: int

class DanistayKeywordSearchRequest(BaseModel): # This is the model the MCP tool will accept
    """Model for keyword-based search request for Danistay."""
    andKelimeler: List[str] = Field(default_factory=list, description="AND keywords")
    orKelimeler: List[str] = Field(default_factory=list, description="OR keywords")
    notAndKelimeler: List[str] = Field(default_factory=list, description="NOT AND keywords")
    notOrKelimeler: List[str] = Field(default_factory=list, description="NOT OR keywords")
    pageSize: int = Field(default=10, ge=1, le=10)
    pageNumber: int = Field(default=1, ge=1)

class DanistayDetailedSearchRequestData(BaseModel): # Internal data model for detailed search payload
    """Internal data model for the detailed search payload's 'data' field."""
    daire: Optional[str] = "" # API expects empty string for None
    esasYil: Optional[str] = ""
    esasIlkSiraNo: Optional[str] = ""
    esasSonSiraNo: Optional[str] = ""
    kararYil: Optional[str] = ""
    kararIlkSiraNo: Optional[str] = ""
    kararSonSiraNo: Optional[str] = ""
    baslangicTarihi: Optional[str] = ""
    bitisTarihi: Optional[str] = ""
    mevzuatNumarasi: Optional[str] = ""
    mevzuatAdi: Optional[str] = ""
    madde: Optional[str] = ""
    siralama: str # Seems mandatory in detailed search payload
    siralamaDirection: str # Seems mandatory
    pageSize: int
    pageNumber: int
    # Note: 'arananKelime' is not in the detailed search payload example provided by user.
    # If it can be included, it should be added here.

class DanistayDetailedSearchRequest(DanistayBaseSearchRequest): # MCP tool will accept this
    """Model for detailed search request for Danistay."""
    daire: Optional[str] = Field(None, description="Chamber")
    esasYil: Optional[str] = Field(None, description="Case year")
    esasIlkSiraNo: Optional[str] = Field(None, description="Start case no")
    esasSonSiraNo: Optional[str] = Field(None, description="End case no")
    kararYil: Optional[str] = Field(None, description="Decision year")
    kararIlkSiraNo: Optional[str] = Field(None, description="Start decision no")
    kararSonSiraNo: Optional[str] = Field(None, description="End decision no")
    baslangicTarihi: Optional[str] = Field(None, description="Start date")
    bitisTarihi: Optional[str] = Field(None, description="End date")
    mevzuatNumarasi: Optional[str] = Field(None, description="Law number")
    mevzuatAdi: Optional[str] = Field(None, description="Law name")
    madde: Optional[str] = Field(None, description="Article")
    siralama: str = Field("1", description="Sort by")
    siralamaDirection: str = Field("desc", description="Direction")
    # Add a general keyword field if detailed search also supports it
    # arananKelime: Optional[str] = Field(None, description="General keyword for detailed search.")


class DanistayApiDecisionEntry(BaseModel):
    """Model for an individual decision entry from the Danistay API search response.
       Based on user-provided response samples for both keyword and detailed search.
    """
    id: str
    # The API response for keyword search uses "daireKurul", detailed search example uses "daire".
    # We use an alias to handle both and map to a consistent field name "chamber".
    chamber: Optional[str] = Field(None, alias="daire", description="Chamber")
    esasNo: Optional[str] = Field(None)
    kararNo: Optional[str] = Field(None)
    kararTarihi: Optional[str] = Field(None)
    arananKelime: Optional[str] = Field(None, description="Keyword")
    # index: Optional[int] = None # Present in response, can be added if needed by MCP tool
    # siraNo: Optional[int] = None # Present in detailed response, can be added

    document_url: Optional[HttpUrl] = Field(None, description="Document URL")

    model_config = ConfigDict(populate_by_name=True, extra='ignore')  # Important for alias to work and ignore extra fields

class DanistayApiResponseInnerData(BaseModel):
    """Model for the inner 'data' object in the Danistay API search response."""
    data: List[DanistayApiDecisionEntry]
    recordsTotal: int
    recordsFiltered: int
    draw: Optional[int] = Field(None, description="Draw counter")

class DanistayApiResponse(BaseModel):
    """Model for the complete search response from the Danistay API."""
    data: Optional[DanistayApiResponseInnerData] = Field(None, description="Response data, can be null when no results found")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata (Meta Veri) from API.")

class DanistayDocumentMarkdown(BaseModel):
    """Model for a Danistay decision document, containing only Markdown content."""
    id: str
    markdown_content: Optional[str] = Field(None, description="The decision content (Karar İçeriği) converted to Markdown.")
    source_url: HttpUrl

class CompactDanistaySearchResult(BaseModel):
    """A compact search result model for the MCP tool to return."""
    decisions: List[DanistayApiDecisionEntry]
    total_records: int
    requested_page: int
    page_size: int