### 执行命令
```shell
 docker run --name demo-proc --rm  -v /data/test:/app/output -d image_name:0.0.1  
```
### 参数说明
-v: 挂载目录(运行后解析excel保存的位置)<br>
--rm: 退出时删除容器<br>
