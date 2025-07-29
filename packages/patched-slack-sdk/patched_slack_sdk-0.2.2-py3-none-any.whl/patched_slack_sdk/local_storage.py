import sqlite3
from typing import Any, Dict, List, NamedTuple, Tuple

import keyring
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import leveldb
import sys
import pathlib
import json
import os


WorkspaceToken = NamedTuple('WorkspaceToken', [('base_url', str), ('token', str), ('name', str)])


class SlackLocalStorage:
    ENCRYPTION_SLACK_KEY_CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'slack_safe_storage_key.txt')

    @classmethod
    def get_workspace_tokens(cls) -> List[WorkspaceToken]:
        """Return a dictionary containing the token (xoxc) and name for each Slack Workspace."""

        if sys.platform == "darwin":
            leveldb_path = '~/Library/Application Support/Slack/Local Storage/leveldb'
            if not pathlib.Path(leveldb_path).expanduser().exists():
                leveldb_path = '~/Library/Containers/com.tinyspeck.slackmacgap/Data/Library/Application Support/Slack/Local Storage/leveldb'
        elif sys.platform.startswith("linux"):
            leveldb_path = '~/.config/Slack/Local Storage/leveldb'
        else:
            raise OSError("slacktokens only works on macOS or Linux.")

        leveldb_path = str(pathlib.Path(leveldb_path).expanduser())

        tmp_path = '/tmp/slack_leveldb'  # temporary path to copy the leveldb file to prevent locking

        if os.path.exists(tmp_path):
            os.system(f'rm -r {tmp_path}')

        os.system(f'cp -r "{leveldb_path}" {tmp_path}')

        db = leveldb.LevelDB(str(pathlib.Path(tmp_path).expanduser()))

        try:
            cfg = next(v for k, v in db.RangeIter() if bytearray(b'localConfig_v2') in k)
        except StopIteration as e:
            raise RuntimeError("Slack's Local Storage not recognised: localConfig not found. Aborting.") from e

        try:
            d = json.loads(cfg[1:])
        except Exception as e:
            raise RuntimeError(
                "Slack's Local Storage not recognised: localConfig not in expected format. Aborting."
            ) from e

        tokens = []
        for v in d['teams'].values():
            tokens.append(WorkspaceToken(base_url=v['url'], token=v['token'], name=v['name']))

        if os.path.exists(tmp_path):
            os.system(f'rm -r {tmp_path}')

        return tokens

    @classmethod
    def get_access_token(cls) -> str:
        """Return the decrypted access token (xoxd) from the Slack cookies."""
        cookies, cookie_database_version = cls.fetch_cookies_from_slack_db()
        encrypted_access_token = next(filter(lambda cookie: cookie['name'] == 'd', cookies))['encrypted_value']
        return cls.decrypt_cookie(encrypted_access_token, cookie_database_version)

    @classmethod
    def fetch_cookies_from_slack_db(cls) -> Tuple[List[Dict[str, Any]], int]:
        if sys.platform == "darwin":
            sqlite_cookie_path = '~/Library/Application Support/Slack/Cookies'
            if not pathlib.Path(sqlite_cookie_path).expanduser().exists():
                sqlite_cookie_path = '~/Library/Containers/com.tinyspeck.slackmacgap/Data/Library/Application Support/Slack/Cookies'
        elif sys.platform.startswith("linux"):
            sqlite_cookie_path = '~/.config/Slack/Cookies'
        else:
            raise OSError("slacktokens only works on macOS or Linux.")
        sqlite_cookie_path = str(pathlib.Path(sqlite_cookie_path).expanduser())
        tmp_path = '/tmp/slack_cookies'  # temporary path to copy the cookies file to prevent locking
        os.system(f'cp "{sqlite_cookie_path}" {tmp_path}')
        conn = sqlite3.connect(tmp_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM cookies")

        cookies = c.fetchall()

        cookie_database_version = 0
        try:
            row = conn.execute("select value from meta where key = 'version';").fetchone()
            if row:
                cookie_database_version = int(row[0])
            else:
                logging.info("cookie database version not found in meta table")
        except sqlite3.OperationalError:
            logging.info("cookie database is missing meta table")

        c.close()
        conn.close()

        if os.path.exists(tmp_path):
            os.system(f'rm {tmp_path}')

        return [dict(row) for row in cookies], cookie_database_version

    @classmethod
    def save_encryption_key(cls, encryption_key):
        with open(cls.ENCRYPTION_SLACK_KEY_CACHE_PATH, 'wb') as f:
            f.write(encryption_key)

    @classmethod
    def get_encryption_key(cls) -> bytes:
        if os.path.exists(cls.ENCRYPTION_SLACK_KEY_CACHE_PATH):
            with open(cls.ENCRYPTION_SLACK_KEY_CACHE_PATH, 'rb') as f:
                encryption_key = f.read()
                if encryption_key: return encryption_key

        if sys.platform == "darwin":
            encryption_key = keyring.get_password('Slack Safe Storage', 'Slack')
            if encryption_key is None:
                raise RuntimeError("Could not find password in Keychain.")
            encryption_key = encryption_key.encode()
            cls.save_encryption_key(encryption_key)
            return encryption_key
        elif sys.platform.startswith("linux"):
            return 'peanuts'.encode()
        else:
            raise OSError("slacktokens only works on macOS or Linux.")

    @classmethod
    def clean_decrypted(cls, decrypted: bytes) -> str:
        r"""Strip padding from decrypted value.

        Remove number indicated by padding
        e.g. if last is '\x0e' then ord('\x0e') == 14, so take off 14.

        Args:
            decrypted: decrypted value
        Returns:
            decrypted, stripped of padding
        """
        last = decrypted[-1]
        if isinstance(last, int):
            return decrypted[:-last].decode("utf8")

        try:
            cleaned = decrypted[: -ord(last)].decode("utf8")
        except UnicodeDecodeError:
            logging.error(
                "UTF8 decoding of the decrypted cookie failed. This is most often "
                "due to attempting decryption with an incorrect key. Consider "
                "searching the pycookiecheat issues for `UnicodeDecodeError`."
            )
            raise

        return cleaned

    @classmethod
    def decrypt_cookie(cls, encrypted_value: bytes, cookie_database_version: int) -> str:
        """Decrypt the cookie value."""
        # Trim off the 'v10' that Chrome/ium prepends
        encrypted_value = encrypted_value[3:]

        # Default values used by both Chrome and Chromium in OSX and Linux
        salt = b'saltysalt'
        iv = b' ' * 16
        length = 16

        encryption_key = cls.get_encryption_key()

        if sys.platform == "darwin":
            iterations = 1003
        elif sys.platform.startswith("linux"):
            iterations = 1
        else:
            raise OSError("slacktokens only works on macOS or Linux.")
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA1(),
                salt=salt,
                length=length,
                iterations=iterations
            )
            key = kdf.derive(encryption_key)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(encrypted_value) + decryptor.finalize()

            if cookie_database_version >= 24:
                # Cookies in database version 24 and later include a SHA256
                # hash of the domain to the start of the encrypted value.
                # https://github.com/chromium/chromium/blob/280265158d778772c48206ffaea788c1030b9aaa/net/extras/sqlite/sqlite_persistent_cookie_store.cc#L223-L224  # noqa
                decrypted = decrypted[32:]

            return cls.clean_decrypted(decrypted)
        except Exception as e:
            if os.path.exists(cls.ENCRYPTION_SLACK_KEY_CACHE_PATH):
                os.remove(cls.ENCRYPTION_SLACK_KEY_CACHE_PATH)
            raise RuntimeError("Could not decrypt cookie.") from e
