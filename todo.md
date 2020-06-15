# redis 数据获取

1.  获取所有企业信息

    ```json
    [
      {
        "name": "企业唯一标识（domain）"
      }
    ]
    ```

2.  获取企业网关信息

    1. 获取所有企业网关信息
    2. 通过 企业`${domain}` 获取某个企业网关信息

    ```json
    {
      "gateway_name": "网关名称（不能有特殊字符）",
      "realm": "网关地址",
      "username": "注册账号",
      "password": "注册密码",
      "register": "是否注册（默认非注册）"
    }
    ```

3.  获取用户内线分机信息

    通过 `${username}@${domain}` 获取用户信息

    ```json
    {
      "id": "用户id",
      "domain": "企业标识",
      "username": "用户名",
      "password": "密码"
    }
    ```

4.  获取系统可执行项目（自动外呼项目）
    通过 `${project_id}` 获取项目信息
    ```json
    {
      "id": "项目id",
      "domain": "企业标识",
      "max_calling": "最大并发",
      "ratio": "系数",
      "status": "执行状态" // 执行 or 暂停
    }
    ```
5.  通过 `${phoneId}` 获取外呼号码

    ```text
    15000000000
    ```

6.  提取项目资料 `redis list` 先进先出队列
    需包含 id, mobile

7.  redis 实时状态管理
    需提供 `free` 实时等待坐席数量
