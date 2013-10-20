# Copyright (C) 2013 Lukas Lalinsky
# Distributed under the MIT license, see the LICENSE file for details.

from flask import Blueprint, g, abort
from sqlalchemy.orm import joinedload, subqueryload
from mbdata.models import (
    ReleaseGroup,
    ReleaseGroupGIDRedirect,
)
from mbdata.utils import get_something_by_gid
from mbdata.api.utils import (
    get_param,
    response_ok,
    response_error,
    make_includes,
)
from mbdata.api.errors import NOT_FOUND_ERROR, INCLUDE_DEPENDENCY_ERROR
from mbdata.api.serialize import serialize_release_group

blueprint = Blueprint('release_group', __name__)


def get_release_group_by_gid(query, gid):
    return get_something_by_gid(query, ReleaseGroupGIDRedirect, gid)


@blueprint.route('/details')
def release_group_details():
    gid = get_param('id', type='uuid', required=True)

    includes_class = make_includes('artist_names', 'artist_credits')
    include = get_param('include', type='enum+', container=includes_class)

    if include.artist_names and include.artist_credits:
        abort(response_error(INCLUDE_DEPENDENCY_ERROR, 'include=artist_names and include=artist_credits are mutually exclusive'))

    query = g.db.query(ReleaseGroup).\
        options(joinedload("type")).\
        options(subqueryload("secondary_types")).\
        options(joinedload("secondary_types.secondary_type", innerjoin=True))

    if include.artist_names or include.artist_credits:
        query = query.options(joinedload("artist_credit", innerjoin=True))
    if include.artist_credits:
        query = query.\
            options(subqueryload("artist_credit.artists")).\
            options(joinedload("artist_credit.artists.artist", innerjoin=True))

    release_group = get_release_group_by_gid(query, gid)
    if release_group is None:
        abort(response_error(NOT_FOUND_ERROR, 'release group not found'))

    return response_ok(release_group=serialize_release_group(release_group, include))

