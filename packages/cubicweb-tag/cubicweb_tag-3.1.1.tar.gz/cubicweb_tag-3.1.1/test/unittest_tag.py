from cubicweb_web.devtools.testlib import WebCWTC


class TagEntityTC(WebCWTC):
    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.tag = cnx.create_entity("Tag", name="x").eid
            self.tag2 = cnx.create_entity("Tag", name="y").eid
            cnx.execute('SET T tags TT WHERE T name "x", TT name "y"')
            cnx.commit()

    def test_dc_title(self):
        with self.admin_access.client_cnx() as cnx:
            tag = cnx.entity_from_eid(self.tag)
            self.assertEqual(tag.dc_title(), "x")

    def test_views_dont_fail(self):
        with self.admin_access.web_request() as req:
            tag = req.entity_from_eid(self.tag)
            tag.view("incontext")
            tag.view("primary")

    def test_boxes_dont_fail(self):
        def w(string, *args, escape=True):
            return string % args if args else string

        with self.admin_access.web_request() as req:
            tag = req.entity_from_eid(self.tag)
            tag2 = req.entity_from_eid(self.tag2)
            self.vreg["ctxcomponents"].select("tags_box", req, rset=tag.cw_rset).render(
                w
            )
            self.vreg["ctxcomponents"].select(
                "similarity_box", req, rset=tag2.cw_rset
            ).render(w)
            self.vreg["ctxcomponents"].select(
                "tagcloud_box", req, rset=tag.cw_rset
            ).render(w)

    def test_json_dont_fail(self):
        with self.admin_access.web_request() as req:
            tag = req.entity_from_eid(self.tag)
            self.vreg["ajax-func"].select("tagged_entity_html", req)("x")
            self.vreg["ajax-func"].select("tagged_entity_html", req, rset=tag.cw_rset)(
                "x"
            )
            entity = req.create_entity("Tag", name="main")
            self.vreg["ajax-func"].select("merge_tags", req)(entity.eid, "x")
            self.vreg["ajax-func"].select("unrelated_merge_tags", req)(entity.eid)

    def test_closest_tags(self):
        with self.admin_access.client_cnx() as cnx:
            cnx.create_entity("Tag", name="main")
            cnx.create_entity("Tag", name="tag1")
            cnx.create_entity("Tag", name="tag2")
            cnx.create_entity("Tag", name="tag3")
            cnx.create_entity("Tag", name="tag4")
            cnx.create_entity("BlogEntry", title="news", content="cubicweb c'est beau")
            cnx.create_entity("BlogEntry", title="yes", content="la vie est belle")
            cnx.create_entity("BlogEntry", title="realy", content="trallalla")
            cnx.create_entity("BlogEntry", title="no", content="c'est vrai")
            cnx.execute('SET T tags B WHERE T name "main" , B title "news"')
            cnx.execute('SET T tags B WHERE T name "main" , B title "yes"')
            cnx.execute('SET T tags B WHERE T name "main" , B title "realy"')
            cnx.execute('SET T tags B WHERE T name "tag1" , B title "news"')
            cnx.execute('SET T tags B WHERE T name "tag1" , B title "yes"')
            cnx.execute('SET T tags B WHERE T name "tag1" , B title "realy"')
            cnx.execute('SET T tags B WHERE T name "tag2" , B title "news"')
            cnx.execute('SET T tags B WHERE T name "tag2" , B title "yes"')
            cnx.execute('SET T tags B WHERE T name "tag3" , B title "realy"')
            cnx.execute('SET T tags B WHERE T name "tag4" , B title "no"')
            compare_tag = cnx.execute(
                "Tag T WHERE T name %(name)s", {"name": "main"}
            ).get_entity(0, 0)
            rset = compare_tag.closest_tags_rset()
            closest_list = [x.name for x in rset.entities()]
            self.assertEqual(closest_list[0], "tag1")
            self.assertEqual(closest_list[1], "tag2")
            self.assertEqual(closest_list[2], "tag3")
            self.assertNotIn("tag4", closest_list)


if __name__ == "__main__":
    import unittest

    unittest.main()
