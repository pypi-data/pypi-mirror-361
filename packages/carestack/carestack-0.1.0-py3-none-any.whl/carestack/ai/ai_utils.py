import logging
from typing import List
import json
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from jose import jwe, jwk
from jose.constants import ALGORITHMS


class AiUtilities:
    """
    A utility class for AI service specific operations like encryption/decryption.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def load_public_key_from_x509_certificate(self, certificate_pem: str) -> dict:
        """
        Loads an RSA public key from a PEM-encoded X.509 certificate and returns it as a JWK.
        """
        try:
            cert = x509.load_pem_x509_certificate(
                certificate_pem.encode("utf-8"), default_backend()
            )
            public_key = cert.public_key()

            if not isinstance(public_key, rsa.RSAPublicKey):
                raise ValueError("The certificate does not contain an RSA public key.")

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            jwk_object = jwk.construct(
                public_pem.decode("utf-8"),  # public_pem is bytes, decode to string
                algorithm=ALGORITHMS.RSA_OAEP_256,  # Specify the algorithm context
            )
            jwk_dict = jwk_object.to_dict()
            return jwk_dict
        except Exception as e:
            self.logger.error(
                f"Error loading public key from certificate: {e}", exc_info=True
            )
            raise RuntimeError(
                f"Failed to load public key from certificate: {e}"
            ) from e

    async def encryption(self, files: List[str]) -> str:
        """
        Encrypts a list of file identifiers using JWE with an RSA public key.
        """
        try:
            certificate_pem = (
                "-----BEGIN CERTIFICATE-----\r\n"
                "MIID6TCCAtECFCuFhek8z9Xvm+QpVXdvsVrC+/qSMA0GCSqGSIb3DQEBCwUAMIGw\r\n"
                "MQswCQYDVQQGEwJJTjESMBAGA1UECAwJVGVsYW5nYW5hMRIwEAYDVQQHDAlIeWRl\r\n"
                "cmFiYWQxJzAlBgNVBAoMHkFjaGFsYSBIZWFsdGggU2VydmljZXMgUHZ0IEx0ZDER\r\n"
                "MA8GA1UECwwIU29mdHdhcmUxDzANBgNVBAMMBkFjaGFsYTEsMCoGCSqGSIb3DQEJ\r\n"
                "ARYdamFnYW4udHVtdWxhQGFjaGFsYWhlYWx0aC5jb20wHhcNMjQxMTEzMTUzNzU0\r\n"
                "WhcNMjQxMjEzMTUzNzU0WjCBsDELMAkGA1UEBhMCSU4xEjAQBgNVBAgMCVRlbGFu\r\n"
                "Z2FuYTESMBAGA1UEBwwJSHlkZXJhYmFkMScwJQYDVQQKDB5BY2hhbGEgSGVhbHRo\r\n"
                "IFNlcnZpY2VzIFB2dCBMdGQxETAPBgNVBAsMCFNvZnR3YXJlMQ8wDQYDVQQDDAZB\r\n"
                "Y2hhbGExLDAqBgkqhkiG9w0BCQEWHWphZ2FuLnR1bXVsYUBhY2hhbGFoZWFsdGgu\r\n"
                "Y29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAty+ydbqnP0gBp39y\r\n"
                "xaFpdLHB9e+wQipf0j+IWW7dlKH1kDwdWLLzdb384vGTB6+Z31144xy+aku0I0e6\r\n"
                "dCubNxKQFj3YFRZBgvlQo/YLRDulHkuJ35CzLdGTLk69Mmn0UAiz+ivaapfmqol+\r\n"
                "U/51l1k7HLWGHAOeVHYLGUcxQTYaYzPecNRH7yn/OTweOZ6vzrQD4g2qzHmzYScP\r\n"
                "+tiOsTg6Ri6bG72084eqXs5bUixClmsYpDq6Eoq5n9uPj+Q5tt98S3JSx1sGpRg2\r\n"
                "KmdbV/xoQ39zMWSkIT8O2tuf5KdfLRvWtm+Q7Af1aQG2U4QedubS/rTCnjIq2AL9\r\n"
                "eAWluQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQA+GdQdGxGDzeAUkfy1iNWx2Wtr\r\n"
                "oMGqpGSgeg5J8dzWcXdwH2Avxh7I9C4yletnuFeKQlCK5GHPvJ2GQCjQ7LEb01BU\r\n"
                "NSJILwfCFMMkjw5COXVXAhp3fr894816YhGW/3+3L3TasKuEG96+bke4rN0yD0v+\r\n"
                "braTqG+fY+hEwwls59jPBrhx97PDoI4RzKPbquAOCcxadJ3gelX0JibOmo9MZLtn\r\n"
                "FhLPTZf8wWJLTdiUiuuiI2YS9/CyN3+pPzznMOEfPDK+593slPwCimubtYb+o/UT\r\n"
                "88tKxqbPGNMWL4CUX9xPTLft8oBkC1OA8oF6kIV0LlJ6LarfhmrWg5BzQqKF\r\n"
                "-----END CERTIFICATE-----\r\n"
            )

            # Load the public key as a JWK from the certificate
            public_jwk = await self.load_public_key_from_x509_certificate(
                certificate_pem
            )

            payload_bytes = json.dumps({"files": files}).encode("utf-8")

            encrypted_payload = jwe.encrypt(
                plaintext=payload_bytes,
                key=public_jwk,  # Use the JWK dictionary
                algorithm=ALGORITHMS.RSA_OAEP_256,
                encryption=ALGORITHMS.A256GCM,
                # 'zip', 'cty', 'kid' could be passed here if needed and supported
            )
            self.logger.debug("Encryption successful.")
            return encrypted_payload.decode("utf-8")

        except Exception as error:
            self.logger.error(f"Failed to encrypt data: {error}", exc_info=True)
            raise RuntimeError(f"Failed to encrypt data: {error}") from error

    # async def decrypt_payload(self, encrypted_data: str, private_key_pem: str) -> Any:
    #     """
    #     Decrypts JWE encrypted data using a PEM-encoded RSA private key.
    #     """
    #     try:
    #         private_key = serialization.load_pem_private_key(
    #             private_key_pem.encode("utf-8"),
    #             password=None,
    #             backend=default_backend(),
    #         )
    #         if not isinstance(private_key, rsa.RSAPrivateKey):
    #             raise ValueError("The provided key is not a valid RSA private key.")

    #         # Construct a JWK from the private key for python-jose
    #         # While python-jose might sometimes work with cryptography objects directly
    #         # for decryption, using jwk.construct is more robust.
    #         private_key_pem_bytes = private_key.private_bytes(
    #             encoding=serialization.Encoding.PEM,
    #             format=serialization.PrivateFormat.PKCS8,
    #             encryption_algorithm=serialization.NoEncryption(),
    #         )
    #         key_jwk = jwk.construct(
    #             private_key_pem_bytes.decode("utf-8"),
    #             algorithm=ALGORITHMS.RSA_OAEP_256,
    #         )
    #         decrypted_payload_bytes = jwe.decrypt(
    #             encrypted_data.encode("utf-8"), key_jwk
    #         )
    #         self.logger.debug("Decryption successful.")
    #         return json.loads(decrypted_payload_bytes.decode("utf-8"))
    #     except Exception as error:
    #         self.logger.error(f"Failed to decrypt data: {error}", exc_info=True)
    #         raise RuntimeError(f"Failed to decrypt data: {error}") from error
