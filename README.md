# Mario Kart 8 NEX server (The python variant)

This is the currently hosted version of Mario Kart 8 on Pretendo Network.
[https://github.com/Newtendo-Network/nex_mario_kart_8](The original repo) has stopped development, this fork exists to continue provide maintenance fixes.

> [!IMPORTANT]
> This server is in **maintenance mode**, no new features will be added. All new efforts should go to [the new repo](https://github.com/PretendoNetwork/mario-kart-8)

# Cloning and building

```shell
git clone --recursive https://www.github.com/EpicUsername12/nex_mario_kart_8.git
```

You need:

- S3 instance
- MongoDB server 6.0+
- Redis server 7.0+

Install Python3 and these libs:

- [NintendoClients](https://github.com/kinnay/NintendoClients)
- ``python -m pip install aioconsole requests pymongo redis grpcio-tools minio``

```shell
python -m grpc_tools.protoc --proto_path=grpc --python_out=. --grpc_python_out=. grpc/amkj_service.proto
```
