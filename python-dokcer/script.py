import docker

client = docker.DockerClient()
container = client.containers.get("magical_meitner")
ip_add = container.attrs['NetworkSettings']['IPAddress']
print(ip_add)
