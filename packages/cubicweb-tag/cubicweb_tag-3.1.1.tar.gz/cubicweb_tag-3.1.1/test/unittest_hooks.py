from cubicweb.devtools.testlib import CubicWebTC


class HooksTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity(
                "BlogEntry", title="une news !", content="cubicweb c'est beau"
            )
            cnx.commit()

    def test_tag_lower_cased(self):
        with self.admin_access.client_cnx() as cnx:
            teid = cnx.execute(
                'INSERT Tag T: T name "ToTo", T tags X ' "WHERE X is BlogEntry"
            )[0][0]
            tname = cnx.execute("Any TN WHERE T eid %(t)s, T name TN", {"t": teid})[0][
                0
            ]
            self.assertEqual(tname, "toto")

            teid = cnx.execute('SET T name "TuTu" WHERE T is Tag')[0][0]
            tname = cnx.execute("Any TN WHERE T eid %(t)s, T name TN", {"t": teid})[0][
                0
            ]
            self.assertEqual(tname, "tutu")

    def test_tag_lower_cased_and_no_comma(self):
        with self.admin_access.client_cnx() as cnx:
            teid = cnx.execute(
                'INSERT Tag T: T name "ToTo, Titi", T tags X ' "WHERE X is BlogEntry"
            )[0][0]
            tname = cnx.execute("Any TN WHERE T eid %(t)s, T name TN", {"t": teid})[0][
                0
            ]
            self.assertEqual(tname, "toto - titi")


if __name__ == "__main__":
    import unittest

    unittest.main()
