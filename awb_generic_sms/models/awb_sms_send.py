from ..helpers.gateway_smart import SmartAPIGateway
from odoo import api, fields, models, exceptions, _
from psycopg2.extensions import AsIs
import datetime
import logging

_logger = logging.getLogger(__name__)


class SMS(models.Model):
    _name = 'awb.sms.send'
    _description = 'SMS Sending'

    def save_history(self, sent_sms):
        self.env['awb.sms.history'].create(sent_sms)

    def _check_sms_gateway(
        self,
        sms_gateway,
        sms_gateway_url,
        sms_gateway_token,
    ):
        if sms_gateway:
            error = []
            if not sms_gateway_url:
                error.append("SMS Gateway Url")
            if not sms_gateway_token:
                error.append("SMS Gateway Token")
            if error:
                raise exceptions.ValidationError(
                    ("%s is/are not set, You can configure this on Settings > Smart SMS Gateway") % (
                        ", ".join(error)
                    )
                )
        else:
            raise exceptions.ValidationError(
                "Inactive SMS Gateway, You can configure this on Settings > Smart SMS Gateway"
            )

    def send_now(
        self,
        sms_id=None,
        recipient_ids=None,
        template_body=None,
        record=None,
        recordset=None,
        template_name=None,
        state=None,
        generic=False,
    ):
        params = self.env['ir.config_parameter'].sudo()
        sms_gateway = params.get_param('smart_gateway')
        sms_gateway_url = params.get_param('smart_gateway_url')
        sms_gateway_token = params.get_param('smart_gateway_token')

        self._check_sms_gateway(
            sms_gateway,
            sms_gateway_url,
            sms_gateway_token,
        )

        if recordset and not generic:
            if not state:
                raise exceptions.ValidationError(
                    ("State parameter is required, Please check server actions")
                )
            if recordset.filtered(lambda rec: rec.state != state).exists():
                raise exceptions.ValidationError(
                    ("Record should be in %s state.") % state
                )

            # Get the raw template and keys for formatting
            raw_template_body, format_keys = self.env['awb.sms.template'].get_template_format(template_name)

            data_recordset = []
            for record in recordset:
                key_value = {}
                # Get key and values of the record
                # Keys is the template for e.g. ${partner_id}
                for key in format_keys:

                    try:
                        value = getattr(record, key)
                    except AttributeError:
                        value = None

                    if value:
                        try:
                            if value.name:
                                value = value.name
                        except AttributeError:
                            # Converts value into currency format
                            if isinstance(value, float):
                                value = "\u20B1 {:,.2f}".format(value)
                            else:
                                # Remove initial 2 digits from atm_ref
                                if key == 'atm_ref':
                                    value = value[2:]

                    raw_data = {key: value or ''}
                    key_value.update(raw_data)

                # Append the data to actual template message
                template_body = raw_template_body.format_map(key_value)
                data_recordset.append(
                    {
                        "record": record,
                        "mobile": record.partner_id.mobile,
                        "template_body": template_body,
                        "partner_id": record.partner_id.id,
                    }
                )
        else:
            data_recordset = recordset

        if data_recordset:
            sms = SmartAPIGateway(
                url=sms_gateway_url,
                token=sms_gateway_token,
                sms_id=sms_id,
                recordset=data_recordset,
                template_name=template_name,
            )
            sent_sms = sms.send()
            self.save_history(sent_sms)
            self.env.cr.commit()

    def send_auto_sms(
        self,
        payment_date_criteria=None,
        due_date_criteria=None,
        template_name=None,
        state=None,
        model=None,
        allow_partial_payment=False,
        limit=None,
        send_only_to_active=None,
        disconnection_subtype=None,
        **kwargs
    ):
        if not state:
            raise exceptions.ValidationError(
                ("State parameter is required")
            )

        domain = []
        domain.append(("state", "=", state))

        if not model or model == 'account.move':
            model = 'account.move'
            domain.append(("type", "=", "out_invoice"))

        # This due_date_criteria for account.move model only
        # Remove due_date_criteria when model parameter is present in scheduled actions
        today = datetime.date.today()
        if due_date_criteria:
            due_date_criteria = today + datetime.timedelta(days=due_date_criteria)
            domain.append(("invoice_date_due", "=", due_date_criteria))
        elif payment_date_criteria:
            payment_date_criteria = today + datetime.timedelta(days=payment_date_criteria)
            domain.append(("payment_date", "=", payment_date_criteria))

        try:
            model = self.env[model]
        except KeyError:
            raise exceptions.ValidationError("Model %s not found. Please check your input." % model)

        # Check if kwargs is in record field
        if kwargs:
            no_field_exist = []

            # Allows filtering by using any existing field from defined model
            for key in kwargs:
                if hasattr(model, key):
                    domain.append((key, "=", kwargs.get(key)))
                else:
                    no_field_exist.append(key)

            if no_field_exist:
                raise exceptions.ValidationError(
                    ("%s field/fields not found in the record") % (
                        ", ".join(no_field_exist)
                    )
                )

        sql = """
            SELECT DISTINCT rec.id
            FROM {sql_model} as rec, sale_subscription as subs
            WHERE
                rec.state = '{state}'
                AND rec.id NOT IN (
                    SELECT sms_history.record_id
                    FROM awb_sms_history as sms_history
                    WHERE (
                        sms_history.record_id IS NOT NULL
                        AND sms_history.record_model = '{model}'
                        AND sms_history.message_type = '{template_name}'
                        AND sms_history.state = 'sent'
                    )
                )
                AND rec.receive_sms = True
        """
        for item in domain:
            sql += """
                AND rec.%s = '%s'
            """ % (item[0], item[2])

        if model._name == 'account.move':
            sql += """
                AND rec.invoice_origin IS NOT NULL
                AND rec.invoice_origin = subs.code
            """

        if allow_partial_payment:
            sql += """
                AND rec.total_balance > (subs.recurring_total / 2)
            """

        if send_only_to_active:
            subscription_active_status = [
                'new', 'upgrade',
                'convert', 'downgrade',
                're-contract', 'pre-termination'
            ]
            sql += """
                AND subs.subscription_status in %s
            """ % (tuple(subscription_active_status),)

        if disconnection_subtype:
            sql += """
                AND subs.subscription_status_subtype = '%s'
            """ % disconnection_subtype

        sql += """
            LIMIT %s
        """ % limit

        sql = sql.format(
            sql_model=AsIs(model._name.replace('.', '_')),
            state=AsIs(state),
            model=AsIs(model._name),
            template_name=AsIs(template_name),
        )

        self.env.cr.execute(sql)

        _logger.info(domain)
        _logger.info(sql)

        results = self.env.cr.fetchall()
        # Converts result ids to a model object
        records = model.browse([rec[0] for rec in results])
        _logger.info(len(records))

        if records:
            self.env['awb.sms.send'].send_now(
                recordset=records,
                template_name=template_name,
                state=state
            )