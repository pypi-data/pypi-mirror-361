import datetime
import typing
from sqlalchemy import select
from caerp.models.user import UserConnections


def get_last_connection(request, user_id: int) -> typing.Optional[datetime.datetime]:
    query = (
        select(UserConnections.month_last_connection)
        .where(UserConnections.user_id == user_id)
        .order_by(UserConnections.month_last_connection.desc())
        .limit(1)
    )
    result = request.dbsession.execute(query).scalar()
    return result
