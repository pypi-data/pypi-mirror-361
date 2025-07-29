"""template automatic tests"""

import unittest

from datetime import date, timedelta

from cubicweb_web.devtools.testlib import AutomaticWebTest, WebCWTC


class AutomaticWebTest(AutomaticWebTest):
    def to_test_etypes(self):
        return set(("Order", "WorkOrder"))

    def list_startup_views(self):
        return ()


class BasicEntitiesTC(WebCWTC):
    def setup_database(self):
        """
        create 1 Order and 3 WorkOrder
        """
        with self.admin_access.repo_cnx() as cnx:
            # WorkOrder
            self.woben = cnx.create_entity(
                "WorkOrder",
                title="Ben",
                begin_date=date(2001, 9, 11),
                end_date=date(2011, 5, 2),
            ).eid
            self.woempty = cnx.create_entity("WorkOrder", title="Empty").eid
            self.woforrest = cnx.create_entity(
                "WorkOrder",
                title="Forrest",
                begin_date=date.today() - timedelta(1),
                end_date=date.today() + timedelta(15),
            ).eid
            # Order
            self.order = cnx.create_entity(
                "Order",
                title="Coltrane",
                budget=100.0,
                split_into=(self.woben, self.woforrest, self.woempty),
            ).eid
            cnx.commit()

    def test_milestone_adapter(self):
        with self.admin_access.repo_cnx() as cnx:
            # Test dates of an empty workorder.
            empty = cnx.entity_from_eid(self.woempty)
            ms_empty = empty.cw_adapt_to("IMileStone")
            self.assertEqual(ms_empty.initial_prevision_date(), date.today())

            # Test dates of an passed workorder, i.e. end date < today.
            ben = cnx.entity_from_eid(self.woben)
            ms_ben = ben.cw_adapt_to("IMileStone")
            self.assertEqual(ms_ben.initial_prevision_date(), ben.end_date)
            self.assertEqual(ms_ben.eta_date(), date.today())

            # Test dates of an 'in progress' (not the state!) workorder, i.e. end
            # date > today
            forrest = cnx.entity_from_eid(self.woforrest)
            ms_forrest = forrest.cw_adapt_to("IMileStone")
            self.assertEqual(ms_forrest.initial_prevision_date(), forrest.end_date)
            self.assertEqual(ms_forrest.eta_date(), forrest.end_date)


if __name__ == "__main__":
    unittest.main()
