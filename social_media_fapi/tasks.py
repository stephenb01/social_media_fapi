import logging

import httpx

from social_media_fapi.config import config

logger = logging.getLogger(__name__)


class APIResponseError(Exception):
    pass


async def send_simple_email(to_email: str, subject: str, body: str):
    logger.debug(f"Sending email to '{to_email[:3]}' with subject '{subject[:20]}'")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
                auth=("api, config.MAILGUN_API_KEY"),
                data={
                    "from": f"Mike <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to": [to_email],
                    "subject": subject,
                    "text": body,
                },
            )
            # The following will raise an exception for 4xx/5xx responses. To catch it need tio use try/excpet for httpx.HTTPStatusError
            response.raise_for_status()

            logger.debug(response.content)

            return response
        except httpx.HTTPStatusError as err:
            raise APIResponseError(
                f"API request failed with status code {err.response.status_code}"
            ) from err


async def send_user_registration_email(email: str, confirmation_url: str):
    return await send_simple_email(
        email,
        "sucessfully signed up",
        (
            f"Hi {email}! You have successfully signed up to the Social Media REST API."
            " Please confirm your email address by clicking on the"
            f" follwoing link: {confirmation_url}"
        ),
    )
