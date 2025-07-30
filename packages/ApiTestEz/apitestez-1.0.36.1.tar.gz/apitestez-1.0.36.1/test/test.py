# -*- coding:utf-8 -*-
# @FileName  :test.py
# @Time      :2024/12/9 11:06
# @Author    :wangfei
# from api_test_ez.ez.mqtt.mqtt import MQTTPublisher, MQTTSubscriber
# import unittest
# import threading
# import time
# import json
# from api_test_ez.core.case import UnitCase
# class TestMQTTCommunication(UnitCase):
#
#     def beforeRequest(self):
#         self.configs['broker'] = 'mqtt-test.qiyou.cn'
#         self.configs['port'] = 8883
#         # self.configs['TESTING_ENV_MQTT_TOPIC'] = "qy_mqtt/+/188B152733D4/20093500020/#"
#         self.request.protocols = "mqtt"
#
#
#
#     def test_publish_and_subscribe(self):
#         # 创建发布者和订阅者实例
#         publisher = MQTTPublisher(
#             self.env,
#             topic="qy_mqtt/ljb/F8272E16D423/150052418000055/dev/firmware/version/get",
#         )
#         subscriber = MQTTSubscriber(
#             self.env, topic="qy_mqtt/ljbapp/F8272E16D423/150052418000055/dev/firmware/version"
#         )
#
#         subscriber_thread = threading.Thread(
#             target=subscriber.subscribe, kwargs={"timeout": 5}
#         )
#         subscriber_thread.start()
#
#         # 等待一秒确保订阅者已经准备好
#         time.sleep(2)
#         payload = {}
#         # 发布消息
#         publisher.publish(json.dumps(payload), 1)
#
#         # 等待订阅线程结束
#         subscriber_thread.join()
#
#         # 验证消息内容
#         for i, msg in enumerate(subscriber.message, 1):
#             self.assertEqual(msg, f"消息: {i}")
#
#     def test_multiple_clients(self):
#         # 测试多个客户端同时通信
#         topics = ["topic1", "topic2", "topic3"]
#         publishers = [
#             MQTTPublisher(broker=self.broker, port=self.port, topic=topic)
#             for topic in topics
#         ]
#         subscribers = [
#             MQTTSubscriber(broker=self.broker, port=self.port, topic=topic)
#             for topic in topics
#         ]
#
#         # 并行订阅和发布
#         for publisher, subscriber in zip(publishers, subscribers):
#             pub_thread = threading.Thread(
#                 target=publisher.publish, kwargs={"max_messages": 2, "interval": 1}
#             )
#             sub_thread = threading.Thread(
#                 target=subscriber.subscribe, kwargs={"timeout": 5}
#             )
#
#             sub_thread.start()
#             time.sleep(1)
#             pub_thread.start()
#
#             pub_thread.join()
#             sub_thread.join()
#
#         # 验证每个主题都收到了消息
#         for subscriber, topic in zip(subscribers, topics):
#             self.assertEqual(
#                 len(subscriber.received_messages), 2, f"Failed for topic {topic}"
#             )
import unittest
from api_test_ez.core.case.frame.frame_unittest import UnitHttpFrame

class Test001(UnitHttpFrame):
    def test_0001(self):
        print("test_0001")
        assert 1 == 1

    def test_0002(self):
        print("test_0002")
        assert 1 == 1

    def test_0003(self):
        print("test_0003")
        assert 1 == 2

    def test_0004(self):
        print("test_0003")
        self.assertEqual(1, 2)


