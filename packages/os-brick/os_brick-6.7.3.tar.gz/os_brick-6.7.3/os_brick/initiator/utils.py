# Copyright 2018 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import contextlib
import os
from typing import Generator

from oslo_concurrency import lockutils
from oslo_concurrency import processutils as putils


def check_manual_scan() -> bool:
    if os.name == 'nt':
        return False

    try:
        putils.execute('grep', '-F', 'node.session.scan', '/sbin/iscsiadm')
    except putils.ProcessExecutionError:
        return False
    return True


ISCSI_SUPPORTS_MANUAL_SCAN = check_manual_scan()


@contextlib.contextmanager
def guard_connection(device: dict) -> Generator:
    """Context Manager handling locks for attach/detach operations.

    In Cinder microversion 3.69 the shared_targets field for volumes are
    tristate:

    - True ==> Lock if iSCSI initiator doesn't support manual scans
    - False ==> Never lock.
    - None ==> Always lock.
    """
    shared = device.get('shared_targets', False)
    if (shared is not None and ISCSI_SUPPORTS_MANUAL_SCAN) or shared is False:
        yield
    else:
        # Cinder passes an OVO, but Nova passes a dictionary, so we use dict
        # key access that works with both.
        with lockutils.lock(device['service_uuid'], 'os-brick-',
                            external=True):
            yield
