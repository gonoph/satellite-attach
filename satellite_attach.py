#!/usr/bin/env python2.7
# Satellite-attach script
# Copyright (C) 2016  Billy Holmes <billy@gonoph.net>
#
# This file is part of Satellite-attach.
# 
# Satellite-attach is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
# 
# Satellite-attach is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# 
# You should have received a copy of the GNU General Public License along with
# Satellite-attach.  If not, see <http://www.gnu.org/licenses/>.

import requests, json, sys, logging

SATELLITE_URL='https://sat1.test.gonoph.net'
SATELLITE_USERNAME='admin'
SATELLITE_PASSWORD='redhat123'
SATELLITE_SUBSCRIPTION_NAME='Employee SKU'
SATELLITE_ORG=1
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

LOG_LEVEL=logging.INFO

def newHandler(lvl, color):
  ch = logging.StreamHandler()
  ch.setLevel(lvl)
  formatter = logging.Formatter('\033[0;{color}m%(levelname)-8s: %(message)s\033[0m'.format(color=30+color))
  ch.setFormatter(formatter)
  f = logging.Filter()
  f.filter = lambda record: record.levelno == lvl		# yes, that's an evil hack
  ch.addFilter(f)
  return ch

def getLogger():
  logger = logging.getLogger(__name__)
  logger.setLevel(LOG_LEVEL)
  logger.addHandler(newHandler(logging.ERROR, RED))
  logger.addHandler(newHandler(logging.WARN, YELLOW))
  logger.addHandler(newHandler(logging.INFO, CYAN))
  logger.addHandler(newHandler(logging.DEBUG, BLUE))
  return logger

log = getLogger()

class KatelloCaller(object):
  def __init__(self, url, username, password):
    self.url = url
    self.auth=requests.auth.HTTPBasicAuth(username, password)
    self.session = requests.Session()
    self.headers={'Content-type': 'application/json'};

  def get(self, path, **kwargs):
    r = self.session.get('{}/{}'.format(self.url, path), auth=self.auth, verify=False, **kwargs)
    log.debug('url: %s', r.url)
    if r.status_code != 200:
      raise IOError('{} {}: {}/{}'.format(r.status_code, r.reason, self.url, path))
    return json.loads(r.text)

  def put(self, path, payload):
    r = self.session.put('{}/{}'.format(self.url, path), auth=self.auth, verify=False, headers=self.headers, data=json.dumps(payload))
    log.debug('url: %s', r.url)
    if r.status_code != 200:
      raise IOError('{} {}: {}/{}'.format(r.status_code, r.reason, self.url, path))
    return json.loads(r.text)

def process(kc, hostid):
  log.warn('processing hostid: %s', hostid)

  j = kc.get('api/hosts/{hostid}/subscriptions'.format(hostid=hostid))
  totals=j['subtotal']
  log.info('Current subs: %s', totals)

  if totals < 1:
    log.info('Adding subs')
    j = kc.get('katello/api/organizations/{organization_id}/subscriptions'.format(organization_id=SATELLITE_ORG), params='search=name="{sub_name}"'.format(sub_name=SATELLITE_SUBSCRIPTION_NAME))
    subid = j['results'][0]['id']
    log.info('Sub id: %s', subid)
    j = kc.put('api/hosts/{hostid}/subscriptions/add_subscriptions'.format(hostid=hostid), {"host_id": 87, "subscriptions": [ { "id": 1, "quantity": 1 } ] })
    log.warn('Added total subs %s', j['subtotal'])
  else:
    log.warn('No need to add subs')

kc = KatelloCaller(SATELLITE_URL, SATELLITE_USERNAME, SATELLITE_PASSWORD)
log.warn('Satellite Org-Id: %s', SATELLITE_ORG)
log.warn('Satellite Subscription: %s', SATELLITE_SUBSCRIPTION_NAME)

if len(sys.argv) <= 1:
  print 'Usage:', sys.argv[0], '"search query"', '# ex: hostgroup=RHEL7-Server'
  sys.exit(1)

j = kc.get('api/organizations/{organization_id}/hosts'.format(organization_id=SATELLITE_ORG), params='search={}'.format(sys.argv[1]))
log.info('Query results: %d', j['subtotal'])

if j['subtotal'] == 0:
  log.error('Search query returned no results!')
  sys.exit(1)

for client in j['results']:
  try:
    process(kc, client['id'])
  except IOError, ex:
    log.error(ex)
