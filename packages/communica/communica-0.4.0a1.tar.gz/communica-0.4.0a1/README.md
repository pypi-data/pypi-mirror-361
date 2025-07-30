# Easy to use IPC library

Sometimes there is no need for complicated,
blazingly fast frameworks with incredible throughput
and even more incredible configuration.
You just want to make your processes **communicate** with each other.
And that's what this library is for.

### Install

`pip install communica`

You can install additional dependencies for various features

`pip install communica[extraname1, extraname2]`
| Extra name | Feature |
| --- | --- |
| orjson | Faster JSON library, it makes available `orjson_dumpb` and `orjson_loadb` functions from `communica.utils` module. |
| adaptix | Makes available `communica.serializers.AdaptixSerializer`, which provides request and response data validation. |
| rabbitmq | Makes available `communica.connectors.RmqConnector`, to use AMQP server for communication. |

### Get communicated

ща так впадлу это писать, давай потом
