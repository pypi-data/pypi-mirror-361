import logging
from bibtexparser.bibdatabase import BibDatabase
from .cross_ref_client import CrossRefClient


class Validator:
    """
    Validates each entry to find its canonical DOI.
    """

    def __init__(self, client: CrossRefClient):
        self.client = client

    def _validate_entry(self, entry: dict) -> str or None:
        """
        Contains the specific logic for validating a single BibTeX entry.

        Args:
            entry: A single entry dictionary.

        Returns:
            The verified DOI string or None if not found/applicable.
        """
        # Rule 1: Books are considered pre-validated.
        if entry.get('ENTRYTYPE') == 'book':
            logging.info(f"Entry '{entry.get('ID')}' is a book, treating as pre-validated.")
            # Return the book's own DOI if it exists, otherwise None.
            return entry.get('doi')

        # Rule 2 (Default): Query the client for all other entry types.
        return self.client.get_doi_for_entry(entry)

    def validate_all(self, database: BibDatabase) -> (BibDatabase, int):
        """
        Orchestrates the validation process for the entire database.
        (This method is now much cleaner)
        """
        logging.info("--- Phase 2a: Validating Entries with Authoritative Source ---")
        validated_count = 0
        for entry in database.entries:
            entry["audit_info"] = {"changes": []}

            # Call the helper method to get the result
            verified_doi = self._validate_entry(entry)

            if verified_doi:
                original_doi = entry.get("doi", "").lower()
                if not original_doi:
                    entry["audit_info"]["changes"].append(
                        f"Added new DOI [{verified_doi}]."
                    )
                elif original_doi != verified_doi.lower():
                    entry["audit_info"]["changes"].append(
                        f"Corrected DOI from [{original_doi}] to [{verified_doi}]."
                    )
                validated_count += 1

            # Store the result, which will be the DOI or None
            entry["verified_doi"] = verified_doi

        logging.info(f"Successfully validated {validated_count} entries with a DOI.")
        return database, validated_count
