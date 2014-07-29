# -*- coding: utf-8 -*-
#
# Copyright © 2014  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2, or (at your option) any later
# version.  This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Any Red Hat trademarks that are incorporated in the source
# code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission
# of Red Hat, Inc.
#

'''
anitya tests for the flask application.
'''

__requires__ = ['SQLAlchemy >= 0.8']
import pkg_resources

import json
import unittest
import sys
import os

import flask

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import anitya
from anitya.lib import model
from tests import Modeltests, create_distro, create_project


class FlaskAdminTest(Modeltests):
    """ Flask tests for the admin controller. """

    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(FlaskAdminTest, self).setUp()

        anitya.app.APP.config['TESTING'] = True
        anitya.SESSION = self.session
        anitya.ui.SESSION = self.session
        anitya.app.SESSION = self.session
        anitya.admin.SESSION = self.session
        anitya.api.SESSION = self.session
        self.app = anitya.app.APP.test_client()

    def test_add_distro(self):
        """ Test the add_distro function. """
        output = self.app.get('/distro/add', follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<li class="errors">Login required</li>' in output.data)

        with anitya.app.APP.test_client() as c:
            with c.session_transaction() as sess:
                sess['openid'] = 'openid_url'
                sess['fullname'] = 'Pierre-Yves C.'
                sess['nickname'] = 'pingou'
                sess['email'] = 'pingou@pingoured.fr'

            output = c.get('/distro/add', follow_redirects=True)
            self.assertEqual(output.status_code, 405)

        with anitya.app.APP.test_client() as c:
            with c.session_transaction() as sess:
                sess['openid'] = 'http://pingou.id.fedoraproject.org/'
                sess['fullname'] = 'Pierre-Yves C.'
                sess['nickname'] = 'pingou'
                sess['email'] = 'pingou@pingoured.fr'

            output = c.get('/distro/add', follow_redirects=True)
            self.assertEqual(output.status_code, 200)

            self.assertTrue('<h1>Add a new disribution</h1>' in output.data)
            self.assertTrue(
                '<td><input id="name" name="name" type="text" value=""></td>'
                in output.data)

            data = {
                'name': 'Debian',
            }

            output = c.post(
                '/distro/add', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue('<h1>Add a new disribution</h1>' in output.data)
            self.assertTrue(
                '<input id="name" name="name" type="text" value="Debian"></'
                in output.data)

            csrf_token = output.data.split(
                'name="csrf_token" type="hidden" value="')[1].split('">')[0]

            data['csrf_token'] = csrf_token

            output = c.post(
                '/distro/add', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<h1>Distribution participating</h1>' in output.data)
            self.assertTrue(
                '<a href="/distro/Debian/edit">' in output.data)

            output = c.post(
                '/distro/add', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                'class="error">Could not add this distro, already exists?</'
                in output.data)
            self.assertTrue(
                '<h1>Distribution participating</h1>' in output.data)
            self.assertTrue(
                '<a href="/distro/Debian/edit">' in output.data)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(FlaskAdminTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE)