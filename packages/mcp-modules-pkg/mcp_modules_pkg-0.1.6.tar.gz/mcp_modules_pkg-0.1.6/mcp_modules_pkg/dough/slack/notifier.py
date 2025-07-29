
import logging
import os

class SlackNotifier:
    """Handles message and file transfers related to Slack without using a Webhook but using a WebClient.

    This class is unified to use WebClient instead of Webhook, and the BI-Apps bot must be invited to the channel.
    The file transfer part is currently on hold as it is not being used.

    Author : 김윤성
    """

    def __init__(self):
        """Initializes the SlackNotifier class with environment-specific settings."""
        self.is_airflow_env = os.environ.get("AIRFLOW_HOME", False)
        if self.is_airflow_env:
            self.slack_conn_id = "slack_bi_apps"
        else:
            self.slack_token = "xoxb-98443562774-1349682328662-6DQ3RFKgK6DzICRI8zKYS7Gj"

    def send_message(self, channel: str, **kwargs):
        """Sends a message to the specified Slack channel, using different methods based on the environment.

        Args:
            channel (str): The channel to send the message to. A BI-Apps bot must be invited to this channel.
            **kwargs: Additional keyword arguments that can be passed to the Slack API. Check https://slack.dev/python-slack-sdk/api-docs/slack_sdk/web/client.html#chat-postmessage for more details.
                - text (str): For sending plain text messages.
                - blocks (list): For sending messages formatted with Block Kit (https://api.slack.com/reference/block-kit/blocks).
        """
        try:
            if self.is_airflow_env:
                self._send_message_airflow(channel, **kwargs)
            else:
                self._send_message_python(channel, **kwargs)
        except Exception as e:
            logging.error(f"Failed to send message: {e}")

    def _send_message_airflow(self, channel: str, **kwargs):
        """Sends a message using the Airflow Slack Hook.

        Args:
            channel (str): The channel to send the message to.
            **kwargs: Additional keyword arguments for the message.
        """
        from airflow.providers.slack.hooks.slack import (
            SlackHook,  # pylint: disable=import-outside-toplevel
        )

        slack_hook = SlackHook(slack_conn_id=self.slack_conn_id)
        kwargs.update({"channel": channel})
        slack_hook.call("chat.postMessage", json=kwargs)

    def _send_message_python(self, channel: str, **kwargs):
        """Sends a message using the Slack SDK directly.

        Args:
            channel (str): The channel to send the message to.
            **kwargs: Additional keyword arguments for the message.
        """
        import slack_sdk  # pylint: disable=import-outside-toplevel

        client = slack_sdk.WebClient(token=self.slack_token)
        client.chat_postMessage(channel=channel, **kwargs)

