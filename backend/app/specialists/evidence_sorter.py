"""
Evidence Sorter AI Specialist

Responsibilities:
- Extract and label attachments from emails and messages
- Categorize documents by type
- Organize evidence for case management systems (Salesforce, etc.)
- Generate metadata for files
- Detect duplicate documents
- Suggest filing structure
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import hashlib


class EvidenceSorterAdapter:
    """Adapter interface for LLM provider"""

    async def complete(self, prompt: str) -> str:  # pragma: no cover
        raise NotImplementedError()


class MockEvidenceSorterAdapter(EvidenceSorterAdapter):
    """Mock adapter for testing"""

    async def complete(self, prompt: str) -> str:
        return (
            "Document Classification:\n"
            "This appears to be a medical record based on the content. "
            "Recommended category: Medical Evidence > Treatment Records. "
            "Suggested tags: medical, treatment, diagnosis."
        )


class EvidenceSorter:
    """
    AI Specialist for organizing and categorizing case documents

    Key capabilities:
    - Classify document types automatically
    - Extract metadata from files
    - Detect and flag duplicates
    - Generate filing recommendations
    - Prepare documents for case management upload
    - Create document summaries
    """

    def __init__(self, llm_adapter: Optional[EvidenceSorterAdapter] = None):
        self.llm = llm_adapter or MockEvidenceSorterAdapter()

        # Document category definitions
        self.document_categories = {
            "medical": {
                "name": "Medical Evidence",
                "subcategories": ["Treatment Records", "Diagnostic Imaging", "Bills", "Prescriptions"],
                "keywords": ["medical", "doctor", "hospital", "MRI", "x-ray", "prescription", "diagnosis"]
            },
            "legal": {
                "name": "Legal Documents",
                "subcategories": ["Pleadings", "Discovery", "Correspondence", "Court Orders"],
                "keywords": ["complaint", "motion", "deposition", "interrogatory", "subpoena", "order"]
            },
            "insurance": {
                "name": "Insurance Documents",
                "subcategories": ["Policy", "Claims", "Correspondence", "Denials"],
                "keywords": ["policy", "claim", "adjuster", "coverage", "limits", "declaration"]
            },
            "employment": {
                "name": "Employment Records",
                "subcategories": ["Pay Stubs", "W2", "Employment Contract", "Termination"],
                "keywords": ["payroll", "salary", "employment", "W-2", "wage", "employer"]
            },
            "photographs": {
                "name": "Photographs/Images",
                "subcategories": ["Injury Photos", "Accident Scene", "Property Damage", "Other"],
                "keywords": ["photo", "image", "picture", ".jpg", ".png", ".jpeg"]
            },
            "correspondence": {
                "name": "Correspondence",
                "subcategories": ["Client Communication", "Opposing Counsel", "Third Party", "Internal"],
                "keywords": ["email", "letter", "fax", "message", "communication"]
            }
        }

    def _classify_document_by_filename(self, filename: str) -> Optional[str]:
        """
        Classify document based on filename

        Returns primary category
        """
        filename_lower = filename.lower()

        # Check each category's keywords
        for category_key, category_info in self.document_categories.items():
            for keyword in category_info["keywords"]:
                if keyword in filename_lower:
                    return category_key

        return None

    def _classify_document_by_content(self, text_content: str) -> Optional[str]:
        """
        Classify document based on text content

        Returns primary category
        """
        content_lower = text_content.lower()

        # Score each category based on keyword matches
        category_scores = {}
        for category_key, category_info in self.document_categories.items():
            score = 0
            for keyword in category_info["keywords"]:
                if keyword in content_lower:
                    score += 1
            if score > 0:
                category_scores[category_key] = score

        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)

        return None

    def _extract_document_metadata(
        self,
        filename: str,
        file_size: Optional[int] = None,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata from document

        Returns structured metadata
        """
        metadata = {
            "filename": filename,
            "file_extension": self._get_file_extension(filename),
            "file_type": self._determine_file_type(filename),
            "file_size_bytes": file_size,
            "extracted_dates": [],
            "extracted_amounts": [],
            "page_count": None  # Would be extracted from actual PDF
        }

        if text_content:
            # Extract dates
            date_pattern = r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'
            dates = re.findall(date_pattern, text_content)
            metadata["extracted_dates"] = list(set(dates))

            # Extract monetary amounts
            money_pattern = r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
            amounts = re.findall(money_pattern, text_content)
            metadata["extracted_amounts"] = list(set(amounts))

            # Estimate page count from content length (rough estimate)
            if text_content:
                metadata["estimated_pages"] = max(1, len(text_content) // 3000)

        return metadata

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension"""
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return "unknown"

    def _determine_file_type(self, filename: str) -> str:
        """Determine file type from extension"""
        extension = self._get_file_extension(filename)

        file_type_map = {
            "pdf": "PDF Document",
            "doc": "Word Document",
            "docx": "Word Document",
            "jpg": "Image",
            "jpeg": "Image",
            "png": "Image",
            "gif": "Image",
            "txt": "Text Document",
            "msg": "Email Message",
            "eml": "Email Message",
            "xlsx": "Spreadsheet",
            "xls": "Spreadsheet"
        }

        return file_type_map.get(extension, "Unknown")

    def _generate_document_hash(self, content: str) -> str:
        """Generate hash for duplicate detection"""
        return hashlib.md5(content.encode()).hexdigest()

    def _suggest_subcategory(
        self,
        primary_category: str,
        text_content: Optional[str] = None
    ) -> Optional[str]:
        """
        Suggest appropriate subcategory

        Args:
            primary_category: Main category
            text_content: Document text content

        Returns:
            Suggested subcategory
        """
        if not primary_category or primary_category not in self.document_categories:
            return None

        category_info = self.document_categories[primary_category]
        subcategories = category_info["subcategories"]

        # Simple keyword matching for subcategory
        # In production, would use more sophisticated NLP
        if text_content and primary_category == "medical":
            if re.search(r'\b(?:MRI|CT|X-ray|imaging)\b', text_content, re.IGNORECASE):
                return "Diagnostic Imaging"
            elif re.search(r'\b(?:bill|invoice|charges|payment)\b', text_content, re.IGNORECASE):
                return "Bills"
            elif re.search(r'\bprescription\b', text_content, re.IGNORECASE):
                return "Prescriptions"
            else:
                return "Treatment Records"

        # Default to first subcategory
        return subcategories[0] if subcategories else None

    async def analyze_document(
        self,
        filename: str,
        text_content: Optional[str] = None,
        file_size: Optional[int] = None,
        case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze and classify a single document

        Args:
            filename: Document filename
            text_content: Extracted text from document
            file_size: File size in bytes
            case_id: Associated case ID

        Returns:
            Classification and metadata
        """
        # Extract basic metadata
        metadata = self._extract_document_metadata(filename, file_size, text_content)

        # Classify by filename
        category_by_filename = self._classify_document_by_filename(filename)

        # Classify by content if available
        category_by_content = None
        if text_content:
            category_by_content = self._classify_document_by_content(text_content)

        # Determine primary category (content takes precedence)
        primary_category = category_by_content or category_by_filename or "correspondence"

        # Suggest subcategory
        subcategory = self._suggest_subcategory(primary_category, text_content)

        # Generate suggested tags
        tags = self._generate_tags(filename, text_content, primary_category)

        # Use LLM for enhanced classification if content available
        llm_classification = None
        if text_content:
            prompt = f"""
            Analyze this document and provide classification guidance.

            Filename: {filename}
            Content preview: {text_content[:500]}...

            Determine:
            1. Document type (medical record, legal pleading, correspondence, etc.)
            2. Key information contained
            3. Suggested filing category
            4. Important dates or amounts
            5. Priority level (high/medium/low)
            """
            llm_response = await self.llm.complete(prompt)
            llm_classification = llm_response

        return {
            "document_id": f"DOC-{int(datetime.utcnow().timestamp() * 1000)}",
            "case_id": case_id,
            "filename": filename,
            "metadata": metadata,
            "classification": {
                "primary_category": primary_category,
                "category_name": self.document_categories[primary_category]["name"],
                "subcategory": subcategory,
                "confidence": 0.85 if category_by_content else 0.65,
                "classification_method": "content_analysis" if category_by_content else "filename_analysis"
            },
            "suggested_tags": tags,
            "llm_classification": llm_classification,
            "filing_recommendation": {
                "folder_path": f"{self.document_categories[primary_category]['name']}/{subcategory or 'General'}",
                "requires_review": category_by_content is None
            },
            "analyzed_at": datetime.utcnow().isoformat()
        }

    def _generate_tags(
        self,
        filename: str,
        text_content: Optional[str],
        category: str
    ) -> List[str]:
        """Generate suggested tags for document"""
        tags = [category]

        combined_text = f"{filename} {text_content or ''}".lower()

        # Add tags based on content
        tag_patterns = {
            "urgent": r'\b(?:urgent|asap|deadline)\b',
            "confidential": r'\b(?:confidential|privileged)\b',
            "settlement": r'\b(?:settlement|demand|offer)\b',
            "medical": r'\b(?:medical|doctor|hospital)\b',
            "billing": r'\b(?:bill|invoice|charge)\b',
            "injury": r'\b(?:injury|accident|crash)\b'
        }

        for tag, pattern in tag_patterns.items():
            if re.search(pattern, combined_text):
                tags.append(tag)

        return list(set(tags))

    async def process_batch(
        self,
        documents: List[Dict[str, Any]],
        case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process multiple documents at once

        Args:
            documents: List of documents to process
                Each dict should have: filename, text_content, file_size
            case_id: Associated case ID

        Returns:
            Batch processing results
        """
        results = []
        duplicates = []
        seen_hashes = set()

        for doc in documents:
            # Analyze document
            analysis = await self.analyze_document(
                filename=doc.get("filename"),
                text_content=doc.get("text_content"),
                file_size=doc.get("file_size"),
                case_id=case_id
            )

            # Check for duplicates
            if doc.get("text_content"):
                doc_hash = self._generate_document_hash(doc["text_content"])
                if doc_hash in seen_hashes:
                    duplicates.append({
                        "filename": doc.get("filename"),
                        "hash": doc_hash,
                        "is_duplicate": True
                    })
                else:
                    seen_hashes.add(doc_hash)

            results.append(analysis)

        # Generate summary
        category_counts = {}
        for result in results:
            cat = result["classification"]["primary_category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "batch_id": f"BATCH-{int(datetime.utcnow().timestamp())}",
            "case_id": case_id,
            "total_documents": len(documents),
            "successfully_processed": len(results),
            "duplicates_found": len(duplicates),
            "category_breakdown": category_counts,
            "documents": results,
            "duplicates": duplicates,
            "processing_summary": {
                "most_common_category": max(category_counts, key=category_counts.get) if category_counts else None,
                "requires_human_review": sum(1 for r in results if r["filing_recommendation"]["requires_review"]),
                "ready_for_filing": sum(1 for r in results if not r["filing_recommendation"]["requires_review"])
            },
            "processed_at": datetime.utcnow().isoformat()
        }

    def generate_salesforce_payload(
        self,
        document_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate Salesforce-compatible payload for document upload

        Args:
            document_analysis: Document analysis result

        Returns:
            Salesforce ContentVersion payload
        """
        # Format for Salesforce ContentVersion object
        return {
            "Title": document_analysis["filename"],
            "PathOnClient": document_analysis["filename"],
            "Description": f"Category: {document_analysis['classification']['category_name']}",
            "Category__c": document_analysis["classification"]["primary_category"],
            "Subcategory__c": document_analysis["classification"]["subcategory"],
            "Tags__c": ";".join(document_analysis["suggested_tags"]),
            "Case_ID__c": document_analysis.get("case_id"),
            "File_Size__c": document_analysis["metadata"].get("file_size_bytes"),
            "Classification_Confidence__c": document_analysis["classification"]["confidence"],
            "Processed_Date__c": document_analysis["analyzed_at"],
            "Requires_Review__c": document_analysis["filing_recommendation"]["requires_review"]
        }
