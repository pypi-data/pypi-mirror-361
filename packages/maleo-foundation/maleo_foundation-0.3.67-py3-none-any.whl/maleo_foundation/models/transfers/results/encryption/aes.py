from pydantic import Field
from maleo_foundation.models.transfers.results.service.general import (
    BaseServiceGeneralResultsTransfers,
)
from maleo_foundation.models.schemas.encryption import MaleoFoundationEncryptionSchemas


class EncryptData(
    MaleoFoundationEncryptionSchemas.Ciphertext,
    MaleoFoundationEncryptionSchemas.InitializationVector,
    MaleoFoundationEncryptionSchemas.Key,
):
    pass


class MaleoFoundationAESEncryptionResultsTransfers:
    class Fail(BaseServiceGeneralResultsTransfers.Fail):
        pass

    class Encrypt(BaseServiceGeneralResultsTransfers.SingleData):
        data: EncryptData = Field(..., description="Single encryption data")

    class Decrypt(BaseServiceGeneralResultsTransfers.SingleData):
        data: MaleoFoundationEncryptionSchemas.Plaintext = Field(
            ..., description="Single decryption data"
        )
