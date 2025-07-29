# Copyright (c) 2022, Red Hat, Inc.
# All Rights Reserved.
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
from oslo_log import log as logging

from os_brick import opts


LOG = logging.getLogger(__name__)


def setup(conf, **kwargs):
    """Setup the os-brick library.

    Service configuration options must have been initialized before this call
    because oslo's lock_path doesn't have a value before that.

    Having kwargs allows us to receive parameters in the future.
    """
    if kwargs:
        LOG.warning('Ignoring arguments %s', kwargs.keys())

    opts.set_defaults(conf)
