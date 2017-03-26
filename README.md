# *cCube* orchestrator

The **orchestrator** is a client for *cCube*, the cloud microservices architecture for Evolutionary Machine Learning (EML) classification.
It creates and provisions the compute units, initiating and directing the symphony of microservices.
It is an interface for *Amazon EC2*, *OpenStack*, and *VirtualBox*.
Given a cloud provider and a configuration file containing the account credentials, the *cCube* **orchestrator** is able to:
  - create the desired nodes on the provider, and provision them with the latest version of *Docker*, using the `node create` command
  - initialize a *Docker Swarm* cluster, by electing one of the nodes as a manager (command `cluster init`)
  - let all other nodes join the cluster as workers, by using the secret token given by the previous command and the name of the manager (`cluster join` command)

## License

*cCube* is licensed under the terms of the [MIT License](https://opensource.org/licenses/MIT).
Please see the [LICENSE](LICENSE.md) file for full details.
