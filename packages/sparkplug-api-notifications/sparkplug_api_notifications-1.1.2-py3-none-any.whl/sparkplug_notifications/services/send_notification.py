import logging
from typing import Any

from django.contrib.auth import get_user_model
from sparkplug_core.utils import (
    send_admin_action,
    send_client_action,
)

from sparkplug_notifications.serializers import DetailSerializer

from .. import enums, models

log = logging.getLogger(__name__)


def send_notification(  # noqa: PLR0913
    *,
    recipient_uuid: str,
    message: str,
    actor_uuid: str | None = None,
    actor_text: str = "",
    target_route: Any = None,  # noqa: ANN401
    target_actor: bool = False,
) -> None:
    actor = None

    log.debug(
        "Attempt to send notification",
        extra={
            "recipient_uuid": recipient_uuid,
            "actor_uuid": actor_uuid,
            "target_actor": target_actor,
        },
    )

    try:
        recipient = (
            get_user_model()
            .objects.filter(is_active=True)
            .get(uuid=recipient_uuid)
        )

        if actor_uuid is not None:
            actor = (
                get_user_model()
                .objects.filter(is_active=True)
                .get(uuid=actor_uuid)
            )

            if target_actor:
                target_route = {
                    "name": "users.read",
                    "params": {
                        "uuid": actor.uuid,
                    },
                }

    except get_user_model().DoesNotExist as e:
        log.exception(
            "User not found - sending notification",
            exc_info=e,
            extra={
                "recipient_uuid": recipient_uuid,
                "actor_uuid": actor_uuid,
            },
        )
        return

    notification = models.Notification.objects.create(
        recipient_id=recipient.id,
        actor=actor,
        actor_text=actor_text,
        message=message,
        target_route=target_route,
    )

    log.debug(
        "Notification created",
        extra={
            "notification_id": notification.id,
            "recipient_id": recipient.id,
            "actor_id": actor.id if actor else None,
        },
    )

    serializer = DetailSerializer(instance=notification)

    if recipient.is_staff:
        log.debug(
            "Sending admin notification",
            extra={
                "recipient_id": recipient.id,
                "notification_id": notification.id,
            },
        )

        send_admin_action(
            action_type=enums.NotificationAction.INSERT,
            payload={"data": serializer.data},
        )

    else:
        log.debug(
            "Sending client notification",
            extra={
                "recipient_id": recipient.id,
                "notification_id": notification.id,
            },
        )

        send_client_action(
            target_uuid=recipient_uuid,
            action_type=enums.NotificationAction.INSERT,
            payload={"data": serializer.data},
        )
