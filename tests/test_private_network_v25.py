import tempfile
import unittest
from pathlib import Path
from backend.app import sync_store

class PrivateNetworkV25Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = sync_store.DB_PATH
        sync_store.DB_PATH = Path(self.tmp.name) / "network.sqlite3"

    def tearDown(self):
        sync_store.DB_PATH = self.old
        self.tmp.cleanup()

    def test_invite_join_login_and_token_principal(self):
        invite = sync_store.create_invite("friends-01", "owner", hours=24, max_uses=1)
        result, error = sync_store.join_network(invite["code"], "amigo_1", "Amigo Uno", "una-clave-muy-segura")
        self.assertIsNone(error)
        self.assertEqual(result["profile"]["tenant_id"], "friends-01")
        principal = sync_store.principal_for_token(result["access_token"])
        self.assertEqual(principal["actor"], "amigo_1")
        login = sync_store.login_network("friends-01", "amigo_1", "una-clave-muy-segura")
        self.assertIsNotNone(login)
        self.assertIsNotNone(sync_store.principal_for_token(result["access_token"]))
        self.assertIsNotNone(sync_store.principal_for_token(login["access_token"]))
        self.assertTrue(sync_store.revoke_session(result["access_token"]))
        self.assertIsNone(sync_store.principal_for_token(result["access_token"]))
        self.assertIsNotNone(sync_store.principal_for_token(login["access_token"]))

    def test_invite_is_single_use_and_wrong_password_fails(self):
        invite = sync_store.create_invite("friends-02", "owner", max_uses=1)
        first, error = sync_store.join_network(invite["code"], "amigo_2", "Amigo Dos", "otra-clave-segura")
        self.assertIsNone(error)
        second, error = sync_store.join_network(invite["code"], "amigo_3", "Amigo Tres", "otra-clave-segura")
        self.assertIsNone(second)
        self.assertIn("utilizada", error)
        self.assertIsNone(sync_store.login_network("friends-02", "amigo_2", "incorrecta-clave"))

    def test_group_messages_and_observations_are_tenant_scoped(self):
        invite = sync_store.create_invite("friends-03", "owner")
        joined, error = sync_store.join_network(invite["code"], "amigo_4", "Amigo Cuatro", "clave-larga-y-segura")
        profile = joined["profile"]
        msg = sync_store.add_message("friends-03", profile["user_id"], profile["display_name"], "Estoy bien")
        obs = sync_store.add_observation("friends-03", profile["user_id"], profile["display_name"], "Vía despejada", "Paso normal", 6.17, -75.58, "route")
        self.assertEqual(sync_store.list_messages("friends-03")[0]["message_id"], msg["message_id"])
        self.assertEqual(len(sync_store.list_messages("other-group")), 0)
        self.assertEqual(sync_store.list_observations("friends-03")[0]["observation_id"], obs["observation_id"])
        self.assertEqual(len(sync_store.list_members("friends-03")), 1)

if __name__ == "__main__":
    unittest.main()
