from .client import APIResource, SpireClient
from .Models.shared_models import Note

class CRMClient():
    
    def __init__(self, client: SpireClient):
        self.client = client
        self.endpoint = "crm"

    def get_note(self, id : int) -> "note":
        """
        Retrieve a note by its ID.

        Args:
            id (int): The ID of the note to retrieve.

        Returns:
            note: The retrieved note
        """
        response = self.client._get(f"/{self.endpoint}/notes/{str(id)}")
        return note.from_json(response, self.client)


class note(APIResource[Note]):
    endpoint = 'crm/notes'
    Model = Note