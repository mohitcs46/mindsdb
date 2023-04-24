import sib_api_v3_sdk

from mindsdb.integrations.handlers.sendinblue_handler.sendinblue_tables import EmailCampaignsTable
from mindsdb.integrations.libs.api_handler import APIHandler
from mindsdb.integrations.libs.response import (
    HandlerStatusResponse as StatusResponse,
)

from mindsdb.utilities import log
from mindsdb_sql import parse_sql


class SendinblueHandler(APIHandler):
    """
    The Sendinblue handler implementation.
    """

    name = 'sendinblue'

    def __init__(self, name: str, **kwargs):
        """
        Initialize the handler.
        Args:
            name (str): name of particular handler instance
            **kwargs: arbitrary keyword arguments.
        """
        super().__init__(name)

        connection_data = kwargs.get("connection_data", {})
        self.connection_data = connection_data
        self.kwargs = kwargs

        self.connection = None
        self.is_connected = False

        email_campaigns_data = EmailCampaignsTable(self)
        self._register_table("email_campaigns", email_campaigns_data)

    def connect(self) -> StatusResponse:
        """
        Set up the connection required by the handler.
        Returns
        -------
        StatusResponse
            connection object
        """
        if self.is_connected is True:
            return self.connection

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.connection_data['api_key']

        self.connection = configuration

        self.is_connected = True

        return self.connection

    def check_connection(self) -> StatusResponse:
        """
        Check connection to the handler.
        Returns:
            HandlerStatusResponse
        """

        response = StatusResponse(False)
        need_to_close = self.is_connected is False

        try:
            configuration = self.connect()
            api_instance = sib_api_v3_sdk.AccountApi(sib_api_v3_sdk.ApiClient(configuration))
            api_instance.get_account()
            response.success = True
        except Exception as e:
            log.logger.error(f'Error connecting to Sendinblue!')
            response.error_message = str(e)
        finally:
            if response.success is True and need_to_close:
                self.disconnect()
            if response.success is False and self.is_connected is True:
                self.is_connected = False

        return response