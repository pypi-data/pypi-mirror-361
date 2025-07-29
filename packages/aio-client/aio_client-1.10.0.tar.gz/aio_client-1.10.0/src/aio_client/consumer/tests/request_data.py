# coding: utf-8

import os


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


TEST_POST_CONSUMER_REQUEST_MESSAGE_ID = "fc6bd70e-a761-11e8-889f-0050568dddf5"


with open(os.path.join(CURRENT_DIR, 'GetConsumerReceipt.json'), 'rb') as f:
    TEST_GET_CONSUMER_RECEIPT_EXAMPLE = f.read()

#"message_id" в GetConsumerReceipt.json
TEST_GET_CONSUMER_RECEIPT_MESSAGE_ID = "c193f1c4-af50-11e8-8c78-0050568dddf5"

with open(os.path.join(CURRENT_DIR, 'GetConsumerRequest.json'), 'rb') as f:
    TEST_GET_CONSUMER_REQUEST_EXAMPLE = f.read()
# "message_id" из GetConsumerReceipt.json
TEST_GET_CONSUMER_REQUEST_MESSAGE_ID = "395d1a92-b564-4aff-8a2d-55cc73af617f"
# "origin_message_id" из GetConsumerRequest.json
TEST_GET_CONSUMER_REQUEST_OR_MESSAGE_ID = TEST_POST_CONSUMER_REQUEST_MESSAGE_ID
