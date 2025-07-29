from base64 import b64decode, b64encode
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from maleo_foundation.enums import BaseEnums
from maleo_foundation.expanded_types.encryption.rsa import (
    MaleoFoundationRSAEncryptionResultsTypes,
)
from maleo_foundation.managers.client.base import ClientService
from maleo_foundation.models.schemas.encryption import MaleoFoundationEncryptionSchemas
from maleo_foundation.models.transfers.parameters.encryption.rsa import (
    MaleoFoundationRSAEncryptionParametersTransfers,
)
from maleo_foundation.models.transfers.results.encryption.rsa import (
    MaleoFoundationRSAEncryptionResultsTransfers,
)
from maleo_foundation.utils.exceptions.service import BaseServiceExceptions
from maleo_foundation.utils.loaders.key.rsa import RSAKeyLoader


RESOURCE = "rsa_encryptions"


class MaleoFoundationRSAEncryptionClientService(ClientService):
    def encrypt(
        self, parameters: MaleoFoundationRSAEncryptionParametersTransfers.Encrypt
    ) -> MaleoFoundationRSAEncryptionResultsTypes.Encrypt:
        """Encrypt a plaintext using RSA algorithm."""

        @BaseServiceExceptions.sync_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            target=BaseEnums.OperationTarget.INTERNAL,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.CREATE,
            create_type=BaseEnums.CreateType.CREATE,
            summary="encrypting plaintext",
            logger=self._logger,
            fail_result_class=MaleoFoundationRSAEncryptionResultsTransfers.Fail,
        )
        def _impl():
            try:
                public_key = RSAKeyLoader.load_with_pycryptodome(
                    type=BaseEnums.KeyType.PUBLIC, extern_key=parameters.key
                )
            except TypeError:
                message = "Invalid key type"
                description = "A public key must be used for encrypting a plaintext"
                other = "Ensure the given key is of type public key"
                return MaleoFoundationRSAEncryptionResultsTransfers.Fail(
                    message=message, description=description, other=other
                )  # type: ignore
            except Exception as e:
                self._logger.error(
                    "Unexpected error occured while trying to import key:\n'%s'",
                    str(e),
                    exc_info=True,
                )
                message = "Invalid key"
                description = "Unexpected error occured while trying to import key"
                other = "Ensure given key is valid"
                return MaleoFoundationRSAEncryptionResultsTransfers.Fail(
                    message=message, description=description, other=other
                )  # type: ignore
            # * Initialize cipher with OAEP padding and SHA-256
            cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
            # * Encrypt the plaintext and return as base64-encoded string
            ciphertext = b64encode(
                cipher.encrypt(parameters.plaintext.encode("utf-8"))
            ).decode("utf-8")
            data = MaleoFoundationEncryptionSchemas.Ciphertext(ciphertext=ciphertext)
            self._logger.info("Plaintext successfully encrypted")
            return MaleoFoundationRSAEncryptionResultsTransfers.Encrypt(
                origin=BaseEnums.OperationOrigin.CLIENT,
                layer=BaseEnums.OperationLayer.SERVICE,
                target=BaseEnums.OperationTarget.INTERNAL,
                resource=RESOURCE,
                operation=BaseEnums.OperationType.CREATE,
                create_type=BaseEnums.CreateType.CREATE,
                data=data,
            )  # type: ignore

        return _impl()

    def decrypt(
        self, parameters: MaleoFoundationRSAEncryptionParametersTransfers.Decrypt
    ) -> MaleoFoundationRSAEncryptionResultsTypes.Decrypt:
        """Decrypt a ciphertext using RSA algorithm."""

        @BaseServiceExceptions.sync_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            target=BaseEnums.OperationTarget.INTERNAL,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.CREATE,
            create_type=BaseEnums.CreateType.CREATE,
            summary="verify single encryption",
            logger=self._logger,
            fail_result_class=MaleoFoundationRSAEncryptionResultsTransfers.Fail,
        )
        def _impl():
            try:
                private_key = RSAKeyLoader.load_with_pycryptodome(
                    type=BaseEnums.KeyType.PRIVATE,
                    extern_key=parameters.key,
                    passphrase=parameters.password,
                )
            except TypeError:
                message = "Invalid key type"
                description = "A private key must be used for decrypting a ciphertext"
                other = "Ensure the given key is of type private key"
                return MaleoFoundationRSAEncryptionResultsTransfers.Fail(
                    message=message, description=description, other=other
                )  # type: ignore
            except Exception as e:
                self._logger.error(
                    "Unexpected error occured while trying to import key:\n'%s'",
                    str(e),
                    exc_info=True,
                )
                message = "Invalid key"
                description = "Unexpected error occured while trying to import key"
                other = "Ensure given key is valid"
                return MaleoFoundationRSAEncryptionResultsTransfers.Fail(
                    message=message, description=description, other=other
                )  # type: ignore
            # * Initialize cipher with OAEP padding and SHA-256
            cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
            # * Decode the base64-encoded ciphertext and then decrypt
            plaintext = cipher.decrypt(b64decode(parameters.ciphertext)).decode()
            data = MaleoFoundationEncryptionSchemas.Plaintext(plaintext=plaintext)
            self._logger.info("Ciphertext successfully decrypted")
            return MaleoFoundationRSAEncryptionResultsTransfers.Decrypt(
                origin=BaseEnums.OperationOrigin.CLIENT,
                layer=BaseEnums.OperationLayer.SERVICE,
                target=BaseEnums.OperationTarget.INTERNAL,
                resource=RESOURCE,
                operation=BaseEnums.OperationType.CREATE,
                create_type=BaseEnums.CreateType.CREATE,
                data=data,
            )  # type: ignore

        return _impl()
