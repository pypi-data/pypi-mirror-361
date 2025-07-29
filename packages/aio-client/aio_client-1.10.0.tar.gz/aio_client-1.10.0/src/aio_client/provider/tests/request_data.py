# coding: utf-8

import os


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(CURRENT_DIR, 'GetProviderRequest.json'), 'rb') as f:
    TEST_GET_PROVIDER_REQUEST_EXAMPLE = f.read()
# "message_type" в "message_type"
TEST_GET_PROVIDER_REQUEST_MESSAGE_TYPE = 'getApplication'

#"message_id" в GetProviderRequest.json
TEST_GET_PROVIDER_REQUEST_MESSAGE_ID = (
    "fc6bd70e-a761-11e8-889f-0050568dddf5")

with open(os.path.join(CURRENT_DIR, 'GetProviderReceipt.json'), 'rb') as f:
    TEST_GET_PROVIDER_RECEIPT_EXAMPLE = f.read()

#"message_id" в GetProviderReceipt.json
TEST_GET_PROVIDER_RECEIPT_MESSAGE_ID = (
    TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)
