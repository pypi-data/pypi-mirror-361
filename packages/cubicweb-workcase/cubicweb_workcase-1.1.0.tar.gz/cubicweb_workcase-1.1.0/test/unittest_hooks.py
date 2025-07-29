
from cubicweb import ValidationError

from cubicweb.devtools.testlib import CubicWebTC


class HooksTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.wc = cnx.create_entity(u'Workcase', ref=u'xyz').eid
            self.wc2 = cnx.create_entity(u'Workcase', ref=u'xyz2').eid
            cnx.commit()

    def test_wp_different_workcase_no_conflict(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(u'INSERT Workpackage WP: WP title "foo", W split_into WP '
                        u'WHERE W eid %(x)s', {'x': self.wc})[0][0]
            cnx.execute(u'INSERT Workpackage WP: WP title "foo", W split_into WP '
                        u'WHERE W eid %(x)s', {'x': self.wc2})[0][0]
            cnx.commit()

    def test_wp_insertion_with_name_conflict(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(u'INSERT Workpackage WP: WP title "foo", W split_into WP '
                        u'WHERE W eid %(x)s', {'x': self.wc})
            cnx.commit()
            self.assertRaises(ValidationError, cnx.execute,
                              u'INSERT Workpackage WP: WP title "foo", W split_into WP '
                              u'WHERE W eid %(x)s', {'x': self.wc})

    def test_wp_update_with_name_conflict(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(u'INSERT Workpackage WP: WP title "foo", W split_into WP '
                        u'WHERE W eid %(x)s', {'x': self.wc})[0][0]
            wp2 = cnx.execute(u'INSERT Workpackage WP: WP title "foo2", W split_into WP '
                              u'WHERE W eid %(x)s', {'x': self.wc})[0][0]
            cnx.commit()
            self.assertRaises(ValidationError, cnx.execute,
                              u'SET X title "foo" WHERE X eid %s' % wp2)

    def test_wp_description_update(self):
        """checks that we can update a WP's description
        without having a UNIQUE violation error
        """
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(u'INSERT Workpackage WP: WP title "foo", W split_into WP '
                        u'WHERE W eid %(x)s', {'x': self.wc})[0][0]
            wp2 = cnx.execute(u'INSERT Workpackage WP: WP title "foo2", W split_into WP '
                              u'WHERE W eid %(x)s', {'x': self.wc})[0][0]
            cnx.commit()
            # we should be able to update description only
            cnx.execute('SET X description "foo" WHERE X eid %s' % wp2)


if __name__ == '__main__':
    import unittest
    unittest.main()
